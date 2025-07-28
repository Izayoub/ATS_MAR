import os
import cv2
import numpy as np
from paddleocr import PaddleOCR
from django.conf import settings
from .base import BaseAIService
import fitz  # PyMuPDF
from PIL import Image
import io
logger = logging.getLogger(__name__)


class OCRService(BaseAIService):
    def __init__(self):
        super().__init__()
        self.model_path = settings.AI_CONFIG.get('PADDLE_OCR_PATH')

    def load_model(self):
        try:
            # Initialiser PaddleOCR avec support multilingue
            self.model = PaddleOCR(
                use_angle_cls=True,
                lang='french',  # Supporte FR par défaut
                show_log=False
            )
            self.is_loaded = True
            logger.info("PaddleOCR model loaded successfully")
        except Exception as e:
            logger.error(f"Erreur lors du chargement PaddleOCR: {e}")
            raise

    def extract_text_from_pdf(self, file_path):
        """Extraction de texte depuis PDF (image ou texte)"""
        text_content = ""

        try:
            # Essayer d'abord l'extraction de texte direct
            doc = fitz.open(file_path)

            for page_num in range(doc.page_count):
                page = doc.get_page(page_num)
                text = page.get_text()

                if text.strip():
                    # PDF avec texte sélectionnable
                    text_content += text + "\n"
                else:
                    # PDF image - utiliser OCR
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))

                    # Convertir en array numpy pour PaddleOCR
                    img_array = np.array(image)
                    ocr_result = self.model.ocr(img_array, cls=True)

                    page_text = ""
                    if ocr_result[0]:
                        for line in ocr_result[0]:
                            page_text += line[1][0] + " "

                    text_content += page_text + "\n"

            doc.close()
            return text_content.strip()

        except Exception as e:
            logger.error(f"Erreur extraction PDF: {e}")
            return ""

    def extract_text_from_image(self, file_path):
        """Extraction de texte depuis image"""
        try:
            self.ensure_model_loaded()

            # Charger l'image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Impossible de charger l'image")

            # Appliquer OCR
            result = self.model.ocr(image, cls=True)

            text_content = ""
            if result[0]:
                for line in result[0]:
                    text_content += line[1][0] + " "

            return text_content.strip()

        except Exception as e:
            logger.error(f"Erreur OCR image: {e}")
            return ""

    def process(self, file_path):
        """Point d'entrée principal pour extraction de texte"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return self.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Format de fichier non supporté: {file_extension}")
