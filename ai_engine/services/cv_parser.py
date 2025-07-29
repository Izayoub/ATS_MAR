# ai_engine/services/cv_parser.py
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any
from .llm_service import LLMService

logger = logging.getLogger(__name__)

class CVParserService:
    def __init__(self):
        self.llm_service = LLMService()
        self.is_loaded = False

    def load_model(self):
        """Charge le modèle TinyLLaMA via LLMService (si nécessaire)"""
        if not self.is_loaded:
            # On peut étendre ici si LLMService nécessite un load_model explicite
            self.is_loaded = True

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extraction simple des contacts (email, téléphone, linkedin) par regex."""
        contact_info = {}

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]

        # Téléphone marocain (exemple)
        phone_patterns = [
            r'\+212[- ]?[0-9]{9}',
            r'0[0-9]{9}',
            r'[0-9]{2}[- ][0-9]{2}[- ][0-9]{2}[- ][0-9]{2}[- ][0-9]{2}'
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

    def extract_skills_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Extraction des compétences techniques et soft skills via TinyLLaMA.

        Utilise LLMService pour envoyer un prompt et récupérer la réponse JSON.
        """
        prompt = f"""
        Analyse ce CV et extrait les compétences techniques et non-techniques.
        
        Texte du CV:
        {text[:2000]}
        
        Réponds uniquement en JSON avec cette structure:
        {{
            "technical_skills": ["Python", "Django", "JavaScript"],
            "soft_skills": ["Leadership", "Communication", "Travail d'équipe"],
            "languages": [
                {{"language": "Français", "level": "Natif"}},
                {{"language": "Anglais", "level": "Courant"}}
            ]
        }}
        """
        try:
            # On utilise generate_resume_summary car TinyLLaMA est optimisé pour générer du texte
            response = self.llm_service.generate_resume_summary(prompt, max_length=500)
            if not response.get('success'):
                logger.error(f"Erreur extraction compétences LLM: {response.get('error')}")
                return {"technical_skills": [], "soft_skills": [], "languages": []}

            generated_text = response.get('summary', '')
            # Extraction JSON dans la réponse (prend la première partie JSON rencontrée)
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                skills_data = json.loads(json_match.group())
                return skills_data
            else:
                logger.warning("Aucun JSON détecté dans la réponse compétences LLM")
                return {"technical_skills": [], "soft_skills": [], "languages": []}
        except Exception as e:
            logger.error(f"Exception lors extraction compétences LLM: {e}")
            return {"technical_skills": [], "soft_skills": [], "languages": []}

    def extract_experience_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Extraction de l'expérience et formation avec TinyLLaMA via LLMService.
        """
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
            response = self.llm_service.generate_resume_summary(prompt, max_length=500)
            if not response.get('success'):
                logger.error(f"Erreur extraction expérience LLM: {response.get('error')}")
                return {"experience": [], "education": [], "total_experience_years": 0}

            generated_text = response.get('summary', '')
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                exp_data = json.loads(json_match.group())
                return exp_data
            else:
                logger.warning("Aucun JSON détecté dans la réponse expérience LLM")
                return {"experience": [], "education": [], "total_experience_years": 0}
        except Exception as e:
            logger.error(f"Exception lors extraction expérience LLM: {e}")
            return {"experience": [], "education": [], "total_experience_years": 0}

    def generate_candidate_summary(self, parsed_data: Dict[str, Any]) -> str:
        """
        Génère un résumé professionnel du candidat via TinyLLaMA (LLMService).
        """
        skills = parsed_data.get('skills', {})
        experience = parsed_data.get('experience', {})

        technical_skills = ', '.join(skills.get('technical_skills', []))
        total_years = experience.get('total_experience_years', 0)
        last_exp = experience.get('experience', [{}])[0] if experience.get('experience') else {}

        last_exp_str = (f"{last_exp.get('title', '')} chez {last_exp.get('company', '')}" if last_exp else "Non spécifiée")

        prompt = f"""
            Génère un résumé professionnel concis (2-3 phrases) pour ce candidat:
            
            Compétences techniques: {technical_skills}
            Années d'expérience: {total_years}
            Dernière expérience: {last_exp_str}
            
            Réponds en français, de manière professionnelle et concise.
            """
        try:
            response = self.llm_service.generate_resume_summary(prompt, max_length=200)
            if response.get('success'):
                return response.get('summary', '').strip()
            else:
                logger.error(f"Erreur génération résumé: {response.get('error')}")
                return "Profil professionnel à analyser."
        except Exception as e:
            logger.error(f"Exception génération résumé: {e}")
            return "Profil professionnel à analyser."

    def process(self, cv_text: str) -> Dict[str, Any]:
        """
        Pipeline complet pour parser un CV:
        - Extraction contacts
        - Extraction compétences & expérience via LLM
        - Génération résumé
        - Horodatage
        """
        try:
            self.load_model()

            contact_info = self.extract_contact_info(cv_text)
            skills_data = self.extract_skills_with_llm(cv_text)
            experience_data = self.extract_experience_with_llm(cv_text)
            summary = self.generate_candidate_summary({
                "skills": skills_data,
                "experience": experience_data
            })

            parsed_data = {
                "contact": contact_info,
                "skills": skills_data,
                "experience": experience_data,
                "ai_summary": summary,
                "parsing_timestamp": datetime.now().isoformat()
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Erreur lors du parsing complet du CV: {e}")
            return {"success": False, "error": str(e)}
