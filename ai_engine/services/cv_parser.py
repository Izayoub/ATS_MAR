import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .llm_service import LLMService

logger = logging.getLogger(__name__)


class CVParserService:
    def __init__(self):
        self.llm_service = LLMService()
        self.is_loaded = False

    def load_model(self):
        """Charge le modèle TinyLLaMA via LLMService"""
        if not self.is_loaded:
            try:
                # Test pour vérifier que le modèle se charge
                test_response = self.llm_service.generate_resume_summary("Test", max_length=10)
                self.is_loaded = test_response.get('success', False)
                if not self.is_loaded:
                    logger.warning("Modèle LLM non disponible, utilisation des fallbacks regex")
            except Exception as e:
                logger.error(f"Erreur chargement modèle LLM: {e}")
                self.is_loaded = False

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extraction des contacts avec patterns étendus"""
        contact_info = {}

        # Email (amélioré)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        if emails:
            contact_info['email'] = emails[0]
            if len(emails) > 1:
                contact_info['all_emails'] = emails

        # Téléphones (patterns internationaux + Maroc)
        phone_patterns = [
            r'\+212[- ]?[5-7][0-9]{8}',  # Maroc mobile
            r'\+212[- ]?[2-9][0-9]{8}',  # Maroc fixe
            r'0[5-7][0-9]{8}',  # Maroc mobile local
            r'0[2-9][0-9]{8}',  # Maroc fixe local
            r'\+33[- ]?[1-9][0-9]{8}',  # France
            r'\+1[- ]?[0-9]{10}',  # USA/Canada
            r'[0-9]{2}[- ][0-9]{2}[- ][0-9]{2}[- ][0-9]{2}[- ][0-9]{2}'  # Format général
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0].strip()
                if len(phones) > 1:
                    contact_info['all_phones'] = phones
                break

        # LinkedIn (patterns étendus)
        linkedin_patterns = [
            r'linkedin\.com/in/[A-Za-z0-9-]+',
            r'linkedin\.com/profile/[A-Za-z0-9-]+',
            r'in/[A-Za-z0-9-]+'
        ]

        for pattern in linkedin_patterns:
            linkedin = re.findall(pattern, text, re.IGNORECASE)
            if linkedin:
                url = linkedin[0]
                if not url.startswith('http'):
                    url = f"https://www.{url}" if url.startswith('linkedin') else f"https://www.linkedin.com/{url}"
                contact_info['linkedin'] = url
                break

        # GitHub
        github_pattern = r'github\.com/[A-Za-z0-9-]+'
        github = re.findall(github_pattern, text, re.IGNORECASE)
        if github:
            contact_info['github'] = f"https://{github[0]}"

        # Adresse (basique)
        address_keywords = ['adresse', 'address', 'domicilié', 'résidant']
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in address_keywords):
                # Prendre cette ligne et potentiellement la suivante
                address_parts = [line.strip()]
                if i + 1 < len(lines) and len(lines[i + 1].strip()) > 0:
                    address_parts.append(lines[i + 1].strip())
                contact_info['address'] = ' '.join(address_parts)
                break

        return contact_info

    def extract_skills_with_llm(self, text: str) -> Dict[str, Any]:
        """Extraction des compétences avec fallback regex si LLM indisponible"""
        if not self.is_loaded:
            logger.info("LLM indisponible, utilisation fallback regex pour compétences")
            return self._extract_skills_fallback(text)

        prompt = f"""
        Analyse ce CV et extrait UNIQUEMENT les compétences techniques et soft skills mentionnées.

        Texte du CV:
        {text[:2000]}

        IMPORTANT: Réponds UNIQUEMENT avec ce JSON exact, sans autre texte:
        {{
            "technical_skills": ["Python", "Django", "JavaScript"],
            "soft_skills": ["Leadership", "Communication", "Travail d'équipe"],
            "languages": [
                {{"language": "Français", "level": "Natif"}},
                {{"language": "Anglais", "level": "Courant"}}
            ],
            "certifications": ["AWS Certified", "PMP"]
        }}
        """

        try:
            response = self.llm_service.generate_resume_summary(prompt, max_length=600)
            if not response.get('success'):
                logger.error(f"Erreur LLM compétences: {response.get('error')}")
                return self._extract_skills_fallback(text)

            generated_text = response.get('summary', '').strip()

            # Nettoyage et extraction JSON plus robuste
            json_text = self._extract_json_from_text(generated_text)
            if json_text:
                skills_data = json.loads(json_text)

                # Validation de la structure
                required_keys = ['technical_skills', 'soft_skills', 'languages']
                if all(key in skills_data for key in required_keys):
                    return skills_data
                else:
                    logger.warning("Structure JSON incomplète, utilisation fallback")
                    return self._extract_skills_fallback(text)
            else:
                logger.warning("Aucun JSON valide détecté, utilisation fallback")
                return self._extract_skills_fallback(text)

        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON compétences: {e}")
            return self._extract_skills_fallback(text)
        except Exception as e:
            logger.error(f"Exception extraction compétences LLM: {e}")
            return self._extract_skills_fallback(text)

    def _extract_skills_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback regex pour l'extraction de compétences"""
        # Compétences techniques communes
        tech_skills_patterns = [
            'python', 'java', 'javascript', 'typescript', 'php', 'c#', 'c++',
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel',
            'mysql', 'postgresql', 'mongodb', 'sql', 'nosql',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux',
            'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch'
        ]

        text_lower = text.lower()
        found_tech_skills = [skill for skill in tech_skills_patterns if skill in text_lower]

        # Langues (patterns basiques)
        language_patterns = {
            'français': r'français|french',
            'anglais': r'anglais|english',
            'arabe': r'arabe|arabic',
            'espagnol': r'espagnol|spanish|español'
        }

        languages = []
        for lang, pattern in language_patterns.items():
            if re.search(pattern, text_lower):
                languages.append({"language": lang.capitalize(), "level": "À évaluer"})

        return {
            "technical_skills": found_tech_skills,
            "soft_skills": [],  # Difficile à extraire avec regex
            "languages": languages,
            "certifications": []
        }

    def extract_experience_with_llm(self, text: str) -> Dict[str, Any]:
        """Extraction expérience avec fallback"""
        if not self.is_loaded:
            return self._extract_experience_fallback(text)

        prompt = f"""
        Analyse ce CV et extrait l'expérience professionnelle et la formation.

        Texte du CV:
        {text[:2500]}

        IMPORTANT: Réponds UNIQUEMENT avec ce JSON exact:
        {{
            "experience": [
                {{
                    "title": "Développeur Full Stack",
                    "company": "TechCorp",
                    "duration": "2021-2023",
                    "description": "Développement applications web",
                    "years": 2
                }}
            ],
            "education": [
                {{
                    "degree": "Master en Informatique",
                    "institution": "ENSIAS",
                    "year": "2020",
                    "field": "Informatique"
                }}
            ],
            "total_experience_years": 3
        }}
        """

        try:
            response = self.llm_service.generate_resume_summary(prompt, max_length=800)
            if not response.get('success'):
                return self._extract_experience_fallback(text)

            generated_text = response.get('summary', '').strip()
            json_text = self._extract_json_from_text(generated_text)

            if json_text:
                exp_data = json.loads(json_text)

                # Validation basique
                if 'experience' in exp_data and 'education' in exp_data:
                    return exp_data

            return self._extract_experience_fallback(text)

        except Exception as e:
            logger.error(f"Exception extraction expérience LLM: {e}")
            return self._extract_experience_fallback(text)

    def _extract_experience_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback basique pour l'expérience"""
        # Extraction très basique des années d'expérience
        years_patterns = [
            r'(\d+)\s*(?:ans?|years?)\s*(?:d.expérience|experience)',
            r'(\d{4})\s*[-–]\s*(\d{4}|présent|present)'
        ]

        total_years = 0
        for pattern in years_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 1:  # Pattern "X ans d'expérience"
                    total_years = max(total_years, int(matches[0]))
                else:  # Pattern "2020-2023"
                    for match in matches:
                        start_year = int(match[0])
                        end_year = 2024 if match[1].lower() in ['présent', 'present'] else int(match[1])
                        total_years += max(0, end_year - start_year)
                break

        return {
            "experience": [],
            "education": [],
            "total_experience_years": total_years
        }

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extrait JSON de manière robuste du texte généré"""
        # Patterns pour trouver JSON
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # JSON simple
            r'\{.*?\}',  # JSON basique
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    # Test si c'est du JSON valide
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

        return None

    def generate_candidate_summary(self, parsed_data: Dict[str, Any]) -> str:
        """Génération de résumé avec fallback"""
        if not self.is_loaded:
            return self._generate_summary_fallback(parsed_data)

        skills = parsed_data.get('skills', {})
        experience = parsed_data.get('experience', {})

        technical_skills = ', '.join(skills.get('technical_skills', [])[:5])  # Top 5
        total_years = experience.get('total_experience_years', 0)
        experiences = experience.get('experience', [])
        last_exp = experiences[0] if experiences else {}

        last_exp_str = (
            f"{last_exp.get('title', '')} chez {last_exp.get('company', '')}"
            if last_exp else "Non spécifiée"
        )

        prompt = f"""
        Génère un résumé professionnel concis (2-3 phrases max) pour ce candidat:

        Compétences principales: {technical_skills}
        Années d'expérience: {total_years}
        Dernière expérience: {last_exp_str}

        Réponds en français, style professionnel et concis. PAS de JSON.
        """

        try:
            response = self.llm_service.generate_resume_summary(prompt, max_length=150)
            if response.get('success'):
                summary = response.get('summary', '').strip()
                # Nettoyage basique
                summary = re.sub(r'^(Résumé|Summary):\s*', '', summary, flags=re.IGNORECASE)
                return summary if summary else self._generate_summary_fallback(parsed_data)
            else:
                return self._generate_summary_fallback(parsed_data)
        except Exception as e:
            logger.error(f"Exception génération résumé: {e}")
            return self._generate_summary_fallback(parsed_data)

    def _generate_summary_fallback(self, parsed_data: Dict[str, Any]) -> str:
        """Génération de résumé basique sans LLM"""
        skills = parsed_data.get('skills', {})
        experience = parsed_data.get('experience', {})

        tech_skills_count = len(skills.get('technical_skills', []))
        total_years = experience.get('total_experience_years', 0)

        if total_years > 0 and tech_skills_count > 0:
            return f"Professionnel avec {total_years} ans d'expérience et {tech_skills_count} compétences techniques identifiées."
        elif tech_skills_count > 0:
            return f"Candidat avec {tech_skills_count} compétences techniques identifiées."
        else:
            return "Profil candidat à analyser en détail."

    def process(self, cv_text: str) -> Dict[str, Any]:
        """Pipeline complet amélioré avec gestion d'erreurs robuste"""
        try:
            # Chargement du modèle
            self.load_model()

            # Validation du texte d'entrée
            if not cv_text or len(cv_text.strip()) < 50:
                return {
                    "success": False,
                    "error": "Texte CV trop court ou vide",
                    "min_length_required": 50
                }

            # Extraction des données
            contact_info = self.extract_contact_info(cv_text)
            skills_data = self.extract_skills_with_llm(cv_text)
            experience_data = self.extract_experience_with_llm(cv_text)

            # Génération du résumé
            summary = self.generate_candidate_summary({
                "skills": skills_data,
                "experience": experience_data
            })

            # Calcul de métadonnées
            metadata = {
                "parsing_timestamp": datetime.now().isoformat(),
                "text_length": len(cv_text),
                "word_count": len(cv_text.split()),
                "llm_used": self.is_loaded,
                "sections_found": {
                    "contact": bool(contact_info),
                    "skills": bool(skills_data.get('technical_skills')),
                    "experience": bool(experience_data.get('experience')),
                    "education": bool(experience_data.get('education'))
                }
            }

            parsed_data = {
                "success": True,
                "contact": contact_info,
                "skills": skills_data,
                "experience": experience_data,
                "ai_summary": summary,
                "metadata": metadata
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Erreur lors du parsing complet du CV: {e}")
            return {
                "success": False,
                "error": str(e),
                "parsing_timestamp": datetime.now().isoformat()
            }