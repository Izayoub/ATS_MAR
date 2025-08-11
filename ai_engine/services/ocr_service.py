import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
from typing import Optional, Dict, List, Tuple
import logging
import re
from pathlib import Path
import os
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

from PIL import Image
import pytesseract  # OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


@dataclass
class ExtractionResult:
    """Résultat d'extraction avec métadonnées"""
    text: str
    pages: int
    method_used: str
    confidence: float
    metadata: Dict
    errors: List[str]

class PDFExtractor:
    """
    Extracteur PDF optimisé avec multiple fallbacks et OCR pour PDF image
    Spécialement conçu pour les CV et offres d'emploi
    """
    
    def __init__(self, log_level: str = "INFO", ocr_lang: str = "eng"):
        self.ocr_lang = ocr_lang  # Langue OCR (ex: 'fra' pour français si installé)
        self.setup_logging(log_level)
        self.extraction_methods = [
            self._extract_with_pdfplumber,
            self._extract_with_pymupdf, 
            self._extract_with_pypdf2,
            self._extract_with_ocr_tesseract  # OCR en dernier recours
        ]
        
    def setup_logging(self, log_level: str):
        """Configure le système de logging"""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('PDFExtractor')
    
    def extract_text_from_pdf(self, file_path: str, method: str = "auto") -> ExtractionResult:
        """
        Extraction intelligente avec fallbacks automatiques et OCR
        
        Args:
            file_path: Chemin vers le fichier PDF
            method: "auto", "pdfplumber", "pymupdf", "pypdf2", "ocr"
        """
        validation_result = self._validate_pdf_file(file_path)
        if not validation_result["valid"]:
            return ExtractionResult("", 0, "none", 0.0, {"file_size": 0}, validation_result["errors"])
        
        if method == "auto":
            return self._extract_with_auto_fallback(file_path)
        else:
            method_map = {
                "pdfplumber": self._extract_with_pdfplumber,
                "pymupdf": self._extract_with_pymupdf,
                "pypdf2": self._extract_with_pypdf2,
                "ocr": self._extract_with_ocr_tesseract
            }
            if method not in method_map:
                return self._create_error_result(f"Méthode inconnue: {method}")
            return method_map[method](file_path)
    
    def _validate_pdf_file(self, file_path: str) -> Dict:
        """Validation robuste du fichier PDF"""
        errors = []
        if not os.path.exists(file_path):
            errors.append(f"Fichier introuvable: {file_path}")
            return {"valid": False, "errors": errors}
        if not file_path.lower().endswith('.pdf'):
            errors.append("Le fichier n'a pas l'extension .pdf")
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                errors.append("Le fichier est vide")
            elif file_size > 50 * 1024 * 1024:
                errors.append("Le fichier est trop volumineux (>50MB)")
        except Exception as e:
            errors.append(str(e))
        try:
            with open(file_path, 'rb') as f:
                if not f.read(8).startswith(b'%PDF'):
                    errors.append("Fichier non PDF valide")
        except Exception as e:
            errors.append(str(e))
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _extract_with_auto_fallback(self, file_path: str) -> ExtractionResult:
        """Extraction avec fallback automatique"""
        best_result = None
        all_errors = []
        for method in self.extraction_methods:
            method_name = method.__name__.replace('_extract_with_', '')
            self.logger.info(f"Tentative extraction avec {method_name}")
            try:
                result = method(file_path)
                result.confidence = self._evaluate_extraction_quality(result.text)
                if best_result is None or result.confidence > best_result.confidence:
                    best_result = result
                    best_result.method_used = method_name
                if result.confidence > 0.8:
                    break
            except Exception as e:
                all_errors.append(f"{method_name} failed: {str(e)}")
                continue
        if best_result:
            best_result.text = self._clean_extracted_text(best_result.text)
            best_result.errors.extend(all_errors)
            return best_result
        return self._create_error_result("Aucune méthode d'extraction réussie")
    
    def _extract_with_pdfplumber(self, file_path: str) -> ExtractionResult:
        """Extraction avec pdfplumber"""
        with pdfplumber.open(file_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    pages_text.append(txt)
            return ExtractionResult("\n\n".join(pages_text), len(pdf.pages), "pdfplumber", 0.0, {}, [])
    
    def _extract_with_pymupdf(self, file_path: str) -> ExtractionResult:
        """Extraction avec PyMuPDF (détection OCR)"""
        doc = fitz.open(file_path)
        pages_text = []
        needs_ocr = False
        for page in doc:
            txt = page.get_text()
            if len(txt.strip()) < 50:  # Texte faible → OCR nécessaire
                needs_ocr = True
            if txt:
                pages_text.append(txt)
        if needs_ocr:
            return self._extract_with_ocr_tesseract(file_path)
        return ExtractionResult("\n\n".join(pages_text), len(doc), "pymupdf", 0.0, {}, [])
    
    def _extract_with_pypdf2(self, file_path: str) -> ExtractionResult:
        """Extraction avec PyPDF2"""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages_text = []
            for page in reader.pages:
                txt = page.extract_text()
                if txt:
                    pages_text.append(txt)
            return ExtractionResult("\n\n".join(pages_text), len(reader.pages), "pypdf2", 0.0, {}, [])
    
    def _extract_with_ocr_tesseract(self, file_path: str) -> ExtractionResult:
        """Extraction OCR complète avec Tesseract"""
        doc = fitz.open(file_path)
        pages_text = []
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_path = f"page_{page_num+1}.png"
            pix.save(img_path)
            img = Image.open(img_path)
            txt = pytesseract.image_to_string(img, lang=self.ocr_lang)
            pages_text.append(txt)
            os.remove(img_path)  # Nettoyage
        return ExtractionResult("\n\n".join(pages_text), len(doc), "ocr_tesseract", 0.0, {}, [])
    
    def _evaluate_extraction_quality(self, text: str) -> float:
        if not text.strip():
            return 0.0
        alpha_ratio = sum(c.isalpha() for c in text) / len(text)
        return min(1.0, alpha_ratio + len(text) / 5000)
    
    def _clean_extracted_text(self, text: str) -> str:
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'[ \t]{2,}', ' ', text)
        return text.strip()
    
    def _create_error_result(self, msg: str) -> ExtractionResult:
        return ExtractionResult("", 0, "none", 0.0, {}, [msg])

# Utilisation rapide
if __name__ == "__main__":
    extractor = PDFExtractor(ocr_lang="fra")  # "fra" si français installé
    test_pdf = r"C:/Users/awati/Desktop/ATS/ATS_MAR/ai_engine/tests/AYOUB_IZEM_CV.pdf"
    if os.path.exists(test_pdf):
        res = extractor.extract_text_from_pdf(test_pdf, method="ocr")
        print(f"📄 Méthode utilisée: {res.method_used}")
        print(f"✅ Confiance: {res.confidence:.2f}")
        print(f"📝 Texte extrait:\n{res.text}")
