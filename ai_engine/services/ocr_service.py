# ai_engine/services/ocr_service.py
import cv2
import numpy as np
from PIL import Image
import re
import logging
from .base import BaseAIService, model_manager

logger = logging.getLogger(__name__)


class OCRService(BaseAIService):
    """Service pour l'extraction de texte des CVs avec PaddleOCR"""

    def __init__(self):
        super().__init__()
        self.model_manager = model_manager

    def extract_text_from_image(self, image_input, lang='en'):
        """
        Extrait le texte d'une image de CV

        Args:
            image_input: Chemin vers l'image, bytes, ou objet PIL Image
            lang: Langue pour l'OCR ('en', 'fr', etc.)

        Returns:
            dict: Résultat de l'extraction avec texte, confiance, etc.
        """
        try:
            # Charger le modèle OCR
            ocr = self.model_manager.load_paddle_ocr(lang)

            # Préprocesser l'image
            processed_image = self._preprocess_image(image_input)

            # Extraction OCR
            results = ocr.ocr(processed_image, cls=True)

            if not results or not results[0]:
                return {
                    'success': False,
                    'text': '',
                    'confidence': 0.0,
                    'blocks': [],
                    'error': 'Aucun texte détecté dans l\'image'
                }

            # Traitement des résultats
            processed_data = self._process_ocr_results(results[0])

            return {
                'success': True,
                'text': processed_data['text'],
                'confidence': processed_data['confidence'],
                'blocks': processed_data['blocks'],
                'language': lang
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction OCR: {e}")
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'blocks': [],
                'error': str(e)
            }

    def extract_structured_resume_data(self, image_input, lang='en'):
        """
        Extrait et structure les données d'un CV

        Args:
            image_input: Image du CV
            lang: Langue du document

        Returns:
            dict: Données structurées du CV
        """
        # Extraction OCR de base
        ocr_result = self.extract_text_from_image(image_input, lang)

        if not ocr_result['success']:
            return ocr_result

        # Structuration des données
        structured_data = self._parse_resume_structure(ocr_result['text'])

        return {
            **ocr_result,
            'structured_data': structured_data
        }

    def _preprocess_image(self, image_input):
        """Préprocesse l'image pour améliorer la qualité OCR"""
        try:
            # Conversion en array numpy
            if isinstance(image_input, str):
                # Chemin de fichier
                image = cv2.imread(image_input)
            elif isinstance(image_input, bytes):
                # Données binaires
                nparr = np.frombuffer(image_input, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif hasattr(image_input, 'read'):
                # Objet file-like
                image_data = image_input.read()
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                # PIL Image ou array numpy
                image = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)

            if image is None:
                raise ValueError("Impossible de charger l'image")

            # Preprocessing pour améliorer l'OCR
            # 1. Conversion en niveaux de gris
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 2. Réduction du bruit
            denoised = cv2.medianBlur(gray, 3)

            # 3. Amélioration du contraste avec CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)

            # 4. Redimensionnement si nécessaire
            height, width = enhanced.shape
            if height < 300 or width < 300:
                scale_factor = max(300 / height, 300 / width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                enhanced = cv2.resize(
                    enhanced,
                    (new_width, new_height),
                    interpolation=cv2.INTER_CUBIC
                )

            # 5. Seuillage adaptatif pour améliorer la lisibilité
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            return binary

        except Exception as e:
            logger.error(f"Erreur lors du préprocessing: {e}")
            raise

    def _process_ocr_results(self, ocr_results):
        """Traite et structure les résultats bruts de PaddleOCR"""
        all_text = []
        all_confidences = []
        blocks = []

        for line in ocr_results:
            if line and len(line) >= 2:
                coordinates = line[0]  # Coordonnées du texte
                text_info = line[1]  # (texte, confiance)

                if text_info and len(text_info) == 2:
                    text, confidence = text_info

                    if text and text.strip():
                        clean_text = text.strip()
                        all_text.append(clean_text)
                        all_confidences.append(confidence)

                        blocks.append({
                            'text': clean_text,
                            'confidence': float(confidence),
                            'coordinates': coordinates,
                            'bbox': self._extract_bbox(coordinates)
                        })

        # Assemblage du texte complet
        full_text = '\n'.join(all_text)

        # Calcul de la confiance moyenne
        avg_confidence = (
            sum(all_confidences) / len(all_confidences)
            if all_confidences else 0.0
        )

        return {
            'text': full_text,
            'confidence': float(avg_confidence),
            'blocks': blocks
        }

    def _extract_bbox(self, coordinates):
        """Extrait la bounding box à partir des coordonnées"""
        if not coordinates or len(coordinates) < 4:
            return None

        x_coords = [point[0] for point in coordinates]
        y_coords = [point[1] for point in coordinates]

        return {
            'x_min': min(x_coords),
            'y_min': min(y_coords),
            'x_max': max(x_coords),
            'y_max': max(y_coords)
        }

    def _parse_resume_structure(self, text):
        """Parse et structure le contenu d'un CV"""
        # Patterns pour extraire des informations spécifiques
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'

        # Extraction des informations de contact
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        phones = re.findall(phone_pattern, text)

        # Identification des sections
        sections = self._identify_resume_sections(text)

        # Extraction des compétences
        skills = self._extract_skills(text, sections.get('skills', []))

        return {
            'contact_info': {
                'emails': emails,
                'phones': [phone.strip() for phone in phones if phone.strip()],
            },
            'sections': sections,
            'skills': skills,
            'raw_text': text,
            'text_length': len(text),
            'word_count': len(text.split())
        }

    def _identify_resume_sections(self, text):
        """Identifie les différentes sections du CV"""
        sections = {}
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Mots-clés pour identifier les sections (multilingue)
        section_keywords = {
            'experience': [
                'experience', 'expérience', 'work experience', 'emploi',
                'employment', 'professional experience', 'career', 'travail'
            ],
            'education': [
                'education', 'formation', 'studies', 'études', 'diplôme',
                'degree', 'university', 'université', 'school', 'école'
            ],
            'skills': [
                'skills', 'compétences', 'competences', 'abilities',
                'technical skills', 'soft skills', 'expertise', 'savoir-faire'
            ],
            'languages': [
                'languages', 'langues', 'idiomas', 'linguistic', 'linguistique'
            ],
            'projects': [
                'projects', 'projets', 'achievements', 'réalisations'
            ],
            'certifications': [
                'certifications', 'certificates', 'certificats', 'awards', 'prix'
            ]
        }

        current_section = 'other'
        sections[current_section] = []

        for line in lines:
            line_lower = line.lower()

            # Vérifier si la ligne est un titre de section
            section_found = False
            for section_name, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section_name
                    if current_section not in sections:
                        sections[current_section] = []
                    section_found = True
                    break

            # Ajouter la ligne à la section courante (sauf si c'est un titre)
            if not section_found and line:
                sections[current_section].append(line)

        # Nettoyage des sections vides
        return {k: v for k, v in sections.items() if v}

    def _extract_skills(self, text, skills_section):
        """Extrait les compétences du CV"""
        skills = []

        # Compétences techniques communes
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'django', 'flask',
            'sql', 'mysql', 'postgresql', 'mongodb', 'docker', 'kubernetes',
            'aws', 'azure', 'git', 'linux', 'html', 'css', 'php',
            'node.js', 'angular', 'vue.js', 'machine learning', 'ai',
            'tensorflow', 'pytorch', 'data analysis', 'pandas', 'numpy'
        ]

        text_lower = text.lower()

        # Recherche des compétences techniques
        found_skills = []
        for skill in tech_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        # Analyse de la section compétences si elle existe
        if skills_section:
            skills_text = ' '.join(skills_section).lower()
            # Extraction basique des compétences listées
            # Cette partie peut être améliorée avec NLP plus avancé
            potential_skills = re.findall(r'\b[a-zA-Z+#.]{2,15}\b', skills_text)
            found_skills.extend([skill for skill in potential_skills if len(skill) > 2])

        return list(set(found_skills))  # Supprime les doublons