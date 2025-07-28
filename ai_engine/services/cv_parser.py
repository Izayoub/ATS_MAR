import re
import json
from datetime import datetime
from .base import BaseAIService
from .llm_service import LLMService
import logging
from django.conf import settings
logger = logging.getLogger(__name__)


class CVParserService(BaseAIService):
    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()

    def load_model(self):
        # Le parsing utilise le service LLM
        self.llm_service.load_model()
        self.is_loaded = True

    def extract_contact_info(self, text):
        """Extraction des informations de contact avec regex"""
        contact_info = {}

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]

        # Téléphone marocain
        phone_patterns = [
            r'\+212[- ]?[0-9]{9}',  # Format international
            r'0[0-9]{9}',  # Format national
            r'[0-9]{2}[- ][0-9]{2}[- ][0-9]{2}[- ][0-9]{2}[- ][0-9]{2}'  # Format avec espaces
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0]
                break

        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin = re.findall(linkedin_pattern, text)
        if linkedin:
            contact_info['linkedin'] = f"https://{linkedin[0]}"

        return contact_info

    def extract_skills_with_llm(self, text):
        """Extraction des compétences avec LLM"""
        prompt = f"""
        Analyse ce CV et extrait les compétences techniques et non-techniques.

        Texte du CV:
        {text[:2000]}  # Limiter pour éviter overflow

        Réponds uniquement en JSON avec cette structure:
        {{
            "technical_skills": ["Python", "Django", "JavaScript"],
            "soft_skills": ["Leadership", "Communication", "Travail d équipe"],
            "languages": [
                {{"language": "Français", "level": "Natif"}},
                {{"language": "Anglais", "level": "Courant"}}
            ]
        }}
        """

        try:
            self.ensure_model_loaded()
            response = self.llm_service.generate_text(prompt)

            # Extraire le JSON de la réponse
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "technical_skills": [],
                    "soft_skills": [],
                    "languages": []
                }
        except Exception as e:
            logger.error(f"Erreur extraction compétences LLM: {e}")
            return {
                "technical_skills": [],
                "soft_skills": [],
                "languages": []
            }

    def extract_experience_with_llm(self, text):
        """Extraction de l'expérience professionnelle avec LLM"""
        prompt = f"""
        Analyse ce CV et extrait l'expérience professionnelle et la formation.

        Texte du CV:
        {text[:2000]}

        Réponds uniquement en JSON:
        {{
            "experience": [
                {{
                    "title": "Développeur Full Stack",
                    "company": "TechCorp",
                    "duration": "2021-2023",
                    "description": "Développement applications web"
                }}
            ],
            "education": [
                {{
                    "degree": "Master en Informatique",
                    "institution": "ENSIAS",
                    "year": "2020"
                }}
            ],
            "total_experience_years": 3
        }}
        """

        try:
            response = self.llm_service.generate_text(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "experience": [],
                    "education": [],
                    "total_experience_years": 0
                }
        except Exception as e:
            logger.error(f"Erreur extraction expérience LLM: {e}")
            return {
                "experience": [],
                "education": [],
                "total_experience_years": 0
            }

    def generate_candidate_summary(self, parsed_data):
        """Génération d'un résumé du candidat avec LLM"""
        skills = parsed_data.get('skills', {})
        experience = parsed_data.get('experience', {})

        prompt = f"""
        Génère un résumé professionnel concis (2-3 phrases) pour ce candidat:

        Compétences techniques: {', '.join(skills.get('technical_skills', []))}
        Années d'expérience: {experience.get('total_experience_years', 0)}
        Dernière expérience: {experience.get('experience', [{}])[0] if experience.get('experience') else 'Non spécifiée'}

        Réponds en français, de manière professionnelle et concise.
        """

        try:
            return self.llm_service.generate_text(prompt)
        except Exception as e:
            logger.error(f"Erreur génération résumé: {e}")
            return "Profil professionnel à analyser."

    def process(self, cv_text):
        """Parsing complet du CV"""
        try:
            self.ensure_model_loaded()

            # 1. Extraction informations de contact
            contact_info = self.extract_contact_info(cv_text)

            # 2. Extraction compétences avec LLM
            skills_data = self.extract_skills_with_llm(cv_text)

            # 3. Extraction expérience avec LLM
            experience_data = self.extract_experience_with_llm(cv_text)

            # 4. Assemblage des données
            parsed_data = {
                'contact': contact_info,
                'skills': skills_data,
                'experience': experience_data,
                'parsing_timestamp': datetime.now().isoformat()
            }

            # 5. Génération résumé
            parsed_data['ai_summary'] = self.generate_candidate_summary(parsed_data)

            return parsed_data

        except Exception as e:
            logger.error(f"Erreur parsing CV: {e}")
            raise