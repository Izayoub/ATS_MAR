# cv_database_manager.py - VERSION REFACTORISÉE
"""
Service pour la gestion des données CV dans PostgreSQL
Architecture modulaire et maintenable
"""

import os
import sys
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod


# Configuration et setup Django
def setup_django_environment():
    """Configuration centralisée de l'environnement Django"""
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_MA.settings')

    import django
    django.setup()


# Setup au niveau module
setup_django_environment()

try:
    from recruitment.models import Candidate
    from django.db import transaction, IntegrityError
except ImportError as e:
    logging.error(f"Erreur d'import Django: {e}")
    sys.exit(1)

# Gestion optionnelle des embeddings
try:
    from sentence_transformers import SentenceTransformer

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    EMBEDDINGS_AVAILABLE = False


@dataclass
class CandidateData:
    """Structure de données pour un candidat"""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    gender: str = ""
    birth_date: Optional[datetime] = None
    address: str = ""
    city: str = ""
    linkedin_url: str = ""
    experience_years: int = 0
    education_level: str = ""
    skills_extracted: List[str] = None
    languages: List[str] = None
    professional_title: str = ""
    ai_summary: str = ""
    cv_embeddings: Optional[Dict] = None

    def __post_init__(self):
        if self.skills_extracted is None:
            self.skills_extracted = []
        if self.languages is None:
            self.languages = []


class DataValidator:
    """Validation des données candidat"""

    @staticmethod
    def validate_email(email: str) -> bool:
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        if not phone or phone == 'nan':
            return ''
        phone_clean = re.sub(r'[^\d+]', '', str(phone))
        if phone_clean.startswith('00'):
            phone_clean = '+' + phone_clean[2:]
        return phone_clean if len(re.sub(r'[^\d]', '', phone_clean)) >= 8 else ''

    @staticmethod
    def validate_name(name: str) -> bool:
        """Vérifie qu'un texte ressemble à un nom de personne"""
        if not name or len(name.strip()) < 2:
            return False

        # Mots-clés de titres professionnels à exclure
        job_keywords = [
            'développeur', 'developer', 'ingénieur', 'engineer', 'chef', 'manager',
            'directeur', 'consultant', 'analyste', 'web', 'full stack'
        ]

        name_lower = name.lower()
        return not any(keyword in name_lower for keyword in job_keywords)


class NameExtractor:
    """Extraction des noms depuis les données CV"""

    def __init__(self):
        self.validator = DataValidator()

    def extract_names_and_title(self, cv_data: Dict) -> Tuple[str, str, str]:
        """
        Extrait prénom, nom et titre professionnel
        Returns: (first_name, last_name, professional_title)
        """
        first_name, last_name, professional_title = '', '', ''

        # 1. Priorité aux coordonnées
        coordonnees = cv_data.get('coordonnees', {})
        if isinstance(coordonnees, dict):
            first_name, last_name = self._extract_from_coordonnees(coordonnees)

        # 2. Titre professionnel depuis titre_candidat
        titre_candidat = cv_data.get('titre_candidat', '').strip()
        if titre_candidat:
            professional_title = self._clean_professional_title(
                titre_candidat, first_name, last_name
            )

        return first_name, last_name, professional_title

    def _extract_from_coordonnees(self, coordonnees: Dict) -> Tuple[str, str]:
        """Extraction depuis les coordonnées"""
        # Recherche nom complet d'abord
        for field in ['nom_complet', 'full_name', 'nom', 'name']:
            if field in coordonnees and coordonnees[field]:
                value = str(coordonnees[field]).strip()
                if self.validator.validate_name(value):
                    return self._parse_full_name(value)

        # Recherche prénom/nom séparément
        first_name = self._find_field_value(
            coordonnees, ['first_name', 'prenom', 'firstname']
        )
        last_name = self._find_field_value(
            coordonnees, ['last_name', 'nom', 'lastname', 'family_name']
        )

        return first_name, last_name

    def _find_field_value(self, data: Dict, field_names: List[str]) -> str:
        """Trouve la première valeur valide parmi les noms de champs"""
        for field in field_names:
            if field in data and data[field]:
                value = str(data[field]).strip()
                if self.validator.validate_name(value):
                    return value
        return ''

    def _parse_full_name(self, full_name: str) -> Tuple[str, str]:
        """Parse un nom complet"""
        if not self.validator.validate_name(full_name):
            return '', ''

        parts = full_name.split()
        if len(parts) == 1:
            return parts[0], ''
        elif len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) >= 3:
            return parts[0], ' '.join(parts[1:])
        return '', ''

    def _clean_professional_title(self, title: str, first_name: str, last_name: str) -> str:
        """Nettoie le titre professionnel en supprimant les noms"""
        clean_title = title
        if first_name and first_name.lower() in clean_title.lower():
            clean_title = clean_title.replace(first_name, '').strip()
        if last_name and last_name.lower() in clean_title.lower():
            clean_title = clean_title.replace(last_name, '').strip()
        return clean_title.strip(' -|:/')


class GenderDetector:
    """Détection automatique du genre"""

    def __init__(self):
        self.male_names = {
            'mohamed', 'ahmed', 'ali', 'omar', 'hassan', 'youssef',
            'pierre', 'jean', 'paul', 'michel', 'alex', 'david'
        }
        self.female_names = {
            'fatima', 'aicha', 'khadija', 'zahra', 'amina', 'sara',
            'marie', 'jeanne', 'anne', 'catherine', 'sophie', 'julie'
        }

    def detect_gender(self, first_name: str, cv_data: Dict = None) -> str:
        """Détecte le genre depuis le prénom"""
        if not first_name:
            return ''

        name_lower = first_name.lower().strip()

        if name_lower in self.male_names:
            return 'M'
        elif name_lower in self.female_names:
            return 'F'

        # Patterns de terminaisons
        if name_lower.endswith(('a', 'e', 'ine', 'elle')):
            return 'F'
        elif name_lower.endswith(('ed', 'ad', 'id', 'oud')):
            return 'M'

        return ''


class EmbeddingGenerator:
    """Générateur d'embeddings pour les CV"""

    def __init__(self):
        self.model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer('BAAI/bge-m3')
            except Exception as e:
                logging.warning(f"Erreur chargement modèle embeddings: {e}")

    def generate_embeddings(self, cv_data: Dict, candidate_data: CandidateData) -> Optional[Dict]:
        """Génère les embeddings structurés"""
        if not self.model:
            return None

        try:
            embeddings = {}

            # Embeddings par section
            embeddings['coordonnees'] = self._embed_coordonnees(cv_data)
            embeddings['experience'] = self._embed_experiences(cv_data)
            embeddings['competences'] = self._embed_skills(cv_data)
            embeddings['formations'] = self._embed_formations(cv_data)

            return {k: v for k, v in embeddings.items() if v}

        except Exception as e:
            logging.error(f"Erreur génération embeddings: {e}")
            return None

    def _embed_coordonnees(self, cv_data: Dict) -> Dict:
        """Embeddings pour les coordonnées"""
        coordonnees = cv_data.get('coordonnees', {})
        if not isinstance(coordonnees, dict):
            return {}

        embeddings = {}
        for field in ['first_name', 'last_name', 'email', 'phone']:
            if field in coordonnees and coordonnees[field]:
                value = str(coordonnees[field]).strip()
                if value:
                    embedding = self.model.encode(f"{field}: {value}", normalize_embeddings=True)
                    embeddings[field] = embedding.tolist()

        return embeddings

    def _embed_experiences(self, cv_data: Dict) -> Dict:
        """Embeddings pour les expériences"""
        experiences = cv_data.get('experience', [])
        if not isinstance(experiences, list):
            return {}

        exp_embeddings = {}
        for i, exp in enumerate(experiences[:5]):
            if isinstance(exp, dict):
                exp_data = {}
                for field in ['poste', 'entreprise', 'description']:
                    if field in exp and exp[field]:
                        value = str(exp[field]).strip()
                        if value:
                            embedding = self.model.encode(f"{field}: {value}", normalize_embeddings=True)
                            exp_data[field] = embedding.tolist()

                if exp_data:
                    exp_embeddings[f'experience_{i}'] = exp_data

        return exp_embeddings

    def _embed_skills(self, cv_data: Dict) -> Dict:
        """Embeddings pour les compétences"""
        skills_embeddings = {}

        # Compétences techniques
        tech_skills = cv_data.get('competences_techniques', [])
        if isinstance(tech_skills, list):
            for skill in tech_skills[:20]:  # Limiter
                if skill and isinstance(skill, str):
                    embedding = self.model.encode(f"competence: {skill}", normalize_embeddings=True)
                    skills_embeddings[f"tech_{skill}"] = embedding.tolist()

        return skills_embeddings

    def _embed_formations(self, cv_data: Dict) -> Dict:
        """Embeddings pour les formations"""
        formations = cv_data.get('formations', [])
        if not isinstance(formations, list):
            return {}

        form_embeddings = {}
        for i, formation in enumerate(formations[:3]):
            if isinstance(formation, dict):
                form_data = {}
                for field in ['diplome', 'etablissement']:
                    if field in formation and formation[field]:
                        value = str(formation[field]).strip()
                        if value:
                            embedding = self.model.encode(f"{field}: {value}", normalize_embeddings=True)
                            form_data[field] = embedding.tolist()

                if form_data:
                    form_embeddings[f'formation_{i}'] = form_data

        return form_embeddings


class CVDataExtractor:
    """Extracteur principal des données CV"""

    def __init__(self):
        self.name_extractor = NameExtractor()
        self.gender_detector = GenderDetector()
        self.embedding_generator = EmbeddingGenerator()
        self.validator = DataValidator()

    def extract(self, cv_data: Dict) -> CandidateData:
        """Extraction principale des données candidat"""
        # Extraction des noms et titre
        first_name, last_name, professional_title = self.name_extractor.extract_names_and_title(cv_data)

        # Coordonnées
        coordonnees = cv_data.get('coordonnees', {})
        email = coordonnees.get('email', '') if isinstance(coordonnees, dict) else ''
        phone = self.validator.clean_phone_number(coordonnees.get('telephone', '')) if isinstance(coordonnees,
                                                                                                  dict) else ''

        # Autres champs
        candidate_data = CandidateData(
            first_name=first_name,
            last_name=last_name,
            professional_title=professional_title,
            email=email if self.validator.validate_email(email) else '',
            phone=phone,
            gender=self.gender_detector.detect_gender(first_name, cv_data),
            experience_years=self._extract_experience_years(cv_data),
            education_level=self._extract_education_level(cv_data),
            skills_extracted=self._extract_skills(cv_data),
            languages=self._extract_languages(cv_data),
            ai_summary=self._generate_summary(cv_data, first_name, last_name, professional_title)
        )

        # Génération des embeddings
        candidate_data.cv_embeddings = self.embedding_generator.generate_embeddings(cv_data, candidate_data)

        return candidate_data

    def _extract_experience_years(self, cv_data: Dict) -> int:
        """Calcul des années d'expérience"""
        # Logique simplifiée - peut être étendue
        exp_years = cv_data.get('experience_years', 0)
        if isinstance(exp_years, (int, float)):
            return max(0, int(exp_years))

        # Fallback: compter les expériences
        experiences = cv_data.get('experience', [])
        return min(len(experiences) * 2, 20)  # Estimation: 2 ans par expérience

    def _extract_education_level(self, cv_data: Dict) -> str:
        """Détermine le niveau d'éducation"""
        formations = cv_data.get('formations', [])
        if not isinstance(formations, list) or not formations:
            return ''

        # Logique simplifiée
        for formation in formations:
            if isinstance(formation, dict):
                diplome = str(formation.get('diplome', '')).lower()
                if 'master' in diplome:
                    return 'Master'
                elif 'licence' in diplome or 'bachelor' in diplome:
                    return 'Licence'
                elif 'bts' in diplome or 'dut' in diplome:
                    return 'BTS/DUT'

        return 'Autre'

    def _extract_skills(self, cv_data: Dict) -> List[str]:
        """Extraction des compétences"""
        all_skills = []

        for skill_type in ['competences_techniques', 'competences_informatiques', 'soft_skills']:
            skills = cv_data.get(skill_type, [])
            if isinstance(skills, list):
                all_skills.extend([str(skill).strip() for skill in skills if skill])

        return list(set(all_skills))  # Dédupliquer

    def _extract_languages(self, cv_data: Dict) -> List[str]:
        """Extraction des langues"""
        langues = cv_data.get('langues', [])
        if not isinstance(langues, list):
            return []

        languages_list = []
        for langue in langues:
            if isinstance(langue, dict):
                nom = langue.get('langue', '') or langue.get('name', '')
                niveau = langue.get('niveau', '') or langue.get('level', '')
                if nom:
                    lang_str = f"{nom} ({niveau})" if niveau else nom
                    languages_list.append(lang_str)
            elif isinstance(langue, str):
                languages_list.append(langue.strip())

        return languages_list

    def _generate_summary(self, cv_data: Dict, first_name: str, last_name: str, professional_title: str) -> str:
        """Génère un résumé intelligent"""
        parts = []

        if professional_title:
            parts.append(professional_title)
        elif first_name or last_name:
            parts.append(f"Profil de {first_name} {last_name}".strip())

        exp_years = self._extract_experience_years(cv_data)
        if exp_years > 0:
            parts.append(f"avec {exp_years} années d'expérience")

        return ". ".join(parts) + "." if parts else "Profil professionnel."


class CVDatabaseManager:
    """Gestionnaire principal pour la sauvegarde des CV en base"""

    def __init__(self, log_level: str = "INFO"):
        self.setup_logging(log_level)
        self.extractor = CVDataExtractor()
        self.stats = {
            "total_processed": 0,
            "successful_saves": 0,
            "failed_saves": 0,
            "duplicates_found": 0
        }

    def setup_logging(self, log_level: str):
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('CVDatabaseManager')

    @transaction.atomic
    def save_candidate(self, cv_data: Dict, source_file: str = None, raw_cv_text: str = '') -> Tuple[
        bool, str, Optional[int]]:
        """
        Sauvegarde un candidat en base
        Returns: (success, message, candidate_id)
        """
        try:
            self.stats["total_processed"] += 1

            # Extraction des données
            candidate_data = self.extractor.extract(cv_data)

            # Vérification des données minimales
            if not self._has_minimum_data(candidate_data):
                error_msg = "Données insuffisantes pour créer un candidat"
                self.logger.error(error_msg)
                self.stats["failed_saves"] += 1
                return False, error_msg, None

            # Vérifier si candidat existe
            existing_candidate = self._find_existing_candidate(candidate_data)

            if existing_candidate:
                return self._update_candidate(existing_candidate, candidate_data)
            else:
                return self._create_candidate(candidate_data, source_file, raw_cv_text)

        except Exception as e:
            error_msg = f"Erreur sauvegarde candidat: {str(e)}"
            self.logger.error(error_msg)
            self.stats["failed_saves"] += 1
            return False, error_msg, None

    def _has_minimum_data(self, candidate_data: CandidateData) -> bool:
        """Vérifie si les données minimales sont présentes"""
        return (
                candidate_data.first_name or
                candidate_data.last_name or
                candidate_data.email or
                candidate_data.professional_title
        )

    def _find_existing_candidate(self, candidate_data: CandidateData) -> Optional[Candidate]:
        """Recherche un candidat existant"""
        # Par email
        if candidate_data.email:
            try:
                return Candidate.objects.get(email=candidate_data.email)
            except Candidate.DoesNotExist:
                pass

        # Par nom complet
        if candidate_data.first_name and candidate_data.last_name:
            try:
                return Candidate.objects.get(
                    first_name=candidate_data.first_name,
                    last_name=candidate_data.last_name
                )
            except Candidate.DoesNotExist:
                pass

        return None

    def _create_candidate(self, candidate_data: CandidateData, source_file: str, raw_cv_text: str) -> Tuple[
        bool, str, int]:
        """Crée un nouveau candidat"""
        try:
            candidate_fields = {
                'first_name': candidate_data.first_name,
                'last_name': candidate_data.last_name,
                'email': candidate_data.email,
                'phone': candidate_data.phone,
                'gender': candidate_data.gender,
                'address': candidate_data.address,
                'city': candidate_data.city,
                'linkedin_url': candidate_data.linkedin_url,
                'experience_years': candidate_data.experience_years,
                'education_level': candidate_data.education_level,
                'skills_extracted': candidate_data.skills_extracted,
                'languages': candidate_data.languages,
                'ai_summary': candidate_data.ai_summary,
            }

            # Ajouter le titre professionnel si le champ existe
            if hasattr(Candidate, 'professional_title'):
                candidate_fields['professional_title'] = candidate_data.professional_title

            # Créer le candidat
            new_candidate = Candidate(**candidate_fields)
            new_candidate.save()

            # Sauvegarder les embeddings séparément si disponibles
            if candidate_data.cv_embeddings:
                self._save_embeddings(new_candidate.id, candidate_data.cv_embeddings)

            success_msg = f"Candidat créé: {new_candidate.first_name} {new_candidate.last_name} (ID: {new_candidate.id})"
            self.logger.info(success_msg)
            self.stats["successful_saves"] += 1
            return True, success_msg, new_candidate.id

        except Exception as e:
            error_msg = f"Erreur création candidat: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None

    def _update_candidate(self, existing_candidate: Candidate, candidate_data: CandidateData) -> Tuple[bool, str, int]:
        """Met à jour un candidat existant"""
        try:
            self.stats["duplicates_found"] += 1

            # Logique de mise à jour sélective
            updated_fields = []

            # Mise à jour des champs vides ou améliorés
            field_mapping = {
                'professional_title': candidate_data.professional_title,
                'address': candidate_data.address,
                'city': candidate_data.city,
                'linkedin_url': candidate_data.linkedin_url,
                'ai_summary': candidate_data.ai_summary,
            }

            for field, new_value in field_mapping.items():
                if hasattr(existing_candidate, field) and new_value:
                    current_value = getattr(existing_candidate, field) or ''
                    if not current_value or len(new_value) > len(current_value):
                        setattr(existing_candidate, field, new_value)
                        updated_fields.append(field)

            # Combiner les compétences
            if candidate_data.skills_extracted:
                current_skills = existing_candidate.skills_extracted or []
                combined_skills = list(set(current_skills + candidate_data.skills_extracted))
                existing_candidate.skills_extracted = combined_skills
                updated_fields.append('skills_extracted')

            # Sauvegarder les embeddings
            if candidate_data.cv_embeddings:
                self._save_embeddings(existing_candidate.id, candidate_data.cv_embeddings)
                updated_fields.append('cv_embeddings')

            existing_candidate.save()

            success_msg = f"Candidat mis à jour: {existing_candidate.first_name} {existing_candidate.last_name} (ID: {existing_candidate.id})"
            if updated_fields:
                success_msg += f" - Champs: {', '.join(updated_fields)}"

            self.logger.info(success_msg)
            self.stats["successful_saves"] += 1
            return True, success_msg, existing_candidate.id

        except Exception as e:
            error_msg = f"Erreur mise à jour candidat: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None

    def _save_embeddings(self, candidate_id: int, embeddings: Dict):
        """Sauvegarde les embeddings séparément"""
        try:
            from django.db import connection
            import json

            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE recruitment_candidate SET cv_embeddings = %s WHERE id = %s",
                    [json.dumps(embeddings), candidate_id]
                )

            self.logger.info(f"Embeddings sauvegardés pour candidat {candidate_id}")

        except Exception as e:
            self.logger.warning(f"Erreur sauvegarde embeddings: {str(e)}")

    def get_statistics(self) -> Dict:
        """Retourne les statistiques"""
        return self.stats.copy()

    def test_database_connection(self) -> Dict:
        """Test la connexion à la base"""
        try:
            count = Candidate.objects.count()
            return {
                "status": "success",
                "message": f"Connexion réussie - {count} candidats en base",
                "candidates_count": count
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur connexion DB: {str(e)}",
                "candidates_count": 0
            }


# Fonction principale pour les tests
def main():
    """Interface en ligne de commande"""
    import argparse

    parser = argparse.ArgumentParser(description="CV Database Manager - Version refactorisée")
    parser.add_argument("command", choices=["test-db", "extract-test"], help="Commande à exécuter")
    parser.add_argument("--log-level", default="INFO", help="Niveau de log")

    args = parser.parse_args()

    db_manager = CVDatabaseManager(log_level=args.log_level)

    if args.command == "test-db":
        result = db_manager.test_database_connection()
        print(f"Test connexion DB: {result['status']}")
        print(f"Message: {result['message']}")

    elif args.command == "extract-test":
        # Test d'extraction avec données d'exemple
        test_data = {
            'titre_candidat': 'Ahmed Benali - Développeur Full Stack',
            'coordonnees': {
                'first_name': 'Ahmed',
                'last_name': 'Benali',
                'email': 'ahmed.benali@example.com',
                'telephone': '+212 6 12 34 56 78'
            },
            'experience': [
                {
                    'poste': 'Développeur Senior',
                    'entreprise': 'TechCorp',
                    'duree': '2 ans',
                    'description': 'Développement applications web avec React et Django'
                }
            ],
            'competences_techniques': ['Python', 'JavaScript', 'React', 'Django'],
            'formations': [
                {
                    'diplome': 'Master en Informatique',
                    'etablissement': 'ENSIAS Rabat'
                }
            ]
        }

        candidate_data = db_manager.extractor.extract(test_data)

        print("=== TEST EXTRACTION ===")
        print(f"Prénom: '{candidate_data.first_name}'")
        print(f"Nom: '{candidate_data.last_name}'")
        print(f"Titre: '{candidate_data.professional_title}'")
        print(f"Email: '{candidate_data.email}'")
        print(f"Téléphone: '{candidate_data.phone}'")
        print(f"Genre: '{candidate_data.gender}'")
        print(f"Expérience: {candidate_data.experience_years} ans")
        print(f"Éducation: '{candidate_data.education_level}'")
        print(f"Compétences: {candidate_data.skills_extracted}")
        print(f"Langues: {candidate_data.languages}")
        print(f"Résumé: '{candidate_data.ai_summary}'")
        print(f"Embeddings générés: {bool(candidate_data.cv_embeddings)}")
        if candidate_data.cv_embeddings:
            print(f"Sections embeddings: {list(candidate_data.cv_embeddings.keys())}")


if __name__ == "__main__":
    main()