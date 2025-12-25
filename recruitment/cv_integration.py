# recruitment/cv_integration.py
"""
Intégration Django CV Parser - Remplissage automatique du modèle Candidate
Adapté pour votre architecture Django ATS_MA
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import transaction
from pathlib import Path

# Import de votre modèle
from .models import Candidate

# Configurez le logger
logger = logging.getLogger('cv_integration')

class CandidateDataExtractor:
    """
    Extracteur spécialisé pour mapper les données CV vers le modèle Candidate Django
    """

    def __init__(self, cv_parser_instance=None):
        """
        Initialise l'extracteur avec une instance de CVParser
        """
        self.cv_parser = cv_parser_instance
        self.logger = logging.getLogger('CandidateExtractor')

        # Patterns de reconnaissance
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+33|0)[1-9](?:[0-9]{8})')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)

    def extract_personal_info_from_cv_data(self, cv_data: Dict) -> Dict:
        """
        Extrait les informations personnelles depuis les données CV parsées
        """
        extracted = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'phone': '',
            'gender': '',
            'birth_date': None,
            'address': '',
            'city': '',
            'linkedin_url': '',
            'experience_years': 0,
            'education_level': '',
            'skills_extracted': [],
            'languages': [],
            'ai_summary': ''
        }

        try:
            # === EXTRACTION NOM/PRÉNOM ===
            titre_candidat = cv_data.get('titre_candidat', '')
            coordonnees = cv_data.get('coordonnees', {})

            if titre_candidat:
                name_parts = self._extract_names_from_title(titre_candidat)
                extracted['first_name'] = name_parts.get('first_name', '')
                extracted['last_name'] = name_parts.get('last_name', '')

            # Compléter depuis les coordonnées si disponibles
            if coordonnees:
                if not extracted['first_name'] and 'prenom' in coordonnees:
                    extracted['first_name'] = str(coordonnees['prenom']).strip()
                if not extracted['last_name'] and 'nom' in coordonnees:
                    extracted['last_name'] = str(coordonnees['nom']).strip()

            # === EXTRACTION EMAIL ===
            email_sources = [
                coordonnees.get('email', ''),
                coordonnees.get('mail', ''),
                str(cv_data.get('email', '')),
                titre_candidat  # Parfois l'email est dans le titre
            ]

            for source in email_sources:
                if source and isinstance(source, str):
                    email_match = self.email_pattern.search(source)
                    if email_match:
                        extracted['email'] = email_match.group().lower()
                        break

            # === EXTRACTION TÉLÉPHONE ===
            phone_sources = [
                coordonnees.get('telephone', ''),
                coordonnees.get('tel', ''),
                coordonnees.get('mobile', ''),
                str(cv_data.get('telephone', ''))
            ]

            for source in phone_sources:
                if source and isinstance(source, str):
                    phone_match = self.phone_pattern.search(source.replace(' ', '').replace('.', '').replace('-', ''))
                    if phone_match:
                        extracted['phone'] = self._format_french_phone(phone_match.group())
                        break

            # === EXTRACTION ADRESSE ===
            address_sources = [
                coordonnees.get('adresse', ''),
                coordonnees.get('address', ''),
                str(cv_data.get('adresse', ''))
            ]

            for source in address_sources:
                if source and isinstance(source, str) and len(source.strip()) > 5:
                    extracted['address'] = source.strip()
                    # Extraire la ville de l'adresse
                    city = self._extract_city_from_address(source)
                    if city:
                        extracted['city'] = city
                    break

            # === EXTRACTION LINKEDIN ===
            linkedin_sources = [
                coordonnees.get('linkedin', ''),
                str(cv_data.get('linkedin', '')),
                str(cv_data.get('profil_linkedin', ''))
            ]

            for source in linkedin_sources:
                if source and isinstance(source, str):
                    linkedin_match = self.linkedin_pattern.search(source)
                    if linkedin_match:
                        linkedin_url = linkedin_match.group()
                        if not linkedin_url.startswith('http'):
                            linkedin_url = 'https://' + linkedin_url
                        extracted['linkedin_url'] = linkedin_url
                        break

            # === EXTRACTION GENRE (OPTIONNEL) ===
            gender = self._guess_gender_from_name(extracted['first_name'])
            if gender:
                extracted['gender'] = gender

            # === EXTRACTION DATE DE NAISSANCE (OPTIONNEL) ===
            birth_date = self._extract_birth_date_from_coordonnees(coordonnees)
            if birth_date:
                extracted['birth_date'] = birth_date

            # === EXTRACTION EXPÉRIENCE ===
            extracted['experience_years'] = cv_data.get('experience_years', 0)

            # === EXTRACTION NIVEAU D'ÉDUCATION ===
            formations = cv_data.get('formations', [])
            education_level = self._determine_education_level(formations)
            extracted['education_level'] = education_level

            # === EXTRACTION COMPÉTENCES ===
            skills = []
            skills_sources = [
                cv_data.get('competences_techniques', []),
                cv_data.get('competences_informatiques', []),
                cv_data.get('soft_skills', [])
            ]

            for source in skills_sources:
                if isinstance(source, list):
                    skills.extend([str(skill).strip() for skill in source if skill])

            # Déduplication et limitation
            extracted['skills_extracted'] = list(dict.fromkeys(skills))[:20]

            # === EXTRACTION LANGUES ===
            langues = cv_data.get('langues', [])
            languages_list = []

            for langue in langues:
                if isinstance(langue, dict):
                    lang_name = langue.get('langue', '')
                    lang_level = langue.get('niveau', '')
                    if lang_name:
                        languages_list.append({
                            'language': lang_name,
                            'level': lang_level
                        })
                elif isinstance(langue, str) and langue.strip():
                    languages_list.append({
                        'language': langue.strip(),
                        'level': 'Non spécifié'
                    })

            extracted['languages'] = languages_list[:10]

            # === GÉNÉRATION RÉSUMÉ IA ===
            if hasattr(self.cv_parser, 'generate_cv_summary'):
                try:
                    summary = self.cv_parser.generate_cv_summary(cv_data)
                    extracted['ai_summary'] = self._format_ai_summary(summary)
                except Exception as e:
                    self.logger.warning(f"Erreur génération résumé IA: {e}")
                    extracted['ai_summary'] = self._create_basic_summary(cv_data)
            else:
                extracted['ai_summary'] = self._create_basic_summary(cv_data)

            return extracted

        except Exception as e:
            self.logger.error(f"Erreur extraction données personnelles: {e}")
            return extracted

    def _extract_names_from_title(self, title: str) -> Dict[str, str]:
        """Extrait prénom et nom depuis le titre candidat"""
        if not title or not isinstance(title, str):
            return {'first_name': '', 'last_name': ''}

        # Nettoyer le titre
        cleaned = re.sub(r'[^\w\s\'-]', ' ', title)
        words = [w.strip() for w in cleaned.split() if w.strip() and len(w) > 1]

        if len(words) == 0:
            return {'first_name': '', 'last_name': ''}
        elif len(words) == 1:
            return {'first_name': words[0].title(), 'last_name': ''}
        elif len(words) == 2:
            return {'first_name': words[0].title(), 'last_name': words[1].upper()}
        else:
            return {
                'first_name': words[0].title(),
                'last_name': ' '.join(words[1:]).upper()
            }

    def _format_french_phone(self, phone: str) -> str:
        """Formate un numéro de téléphone français"""
        digits = re.sub(r'[^\d]', '', phone)

        if digits.startswith('33') and len(digits) == 11:
            digits = '0' + digits[2:]

        if len(digits) == 10 and digits.startswith('0'):
            return f"{digits[:2]}.{digits[2:4]}.{digits[4:6]}.{digits[6:8]}.{digits[8:]}"

        return digits

    def _extract_city_from_address(self, address: str) -> str:
        """Extrait la ville depuis une adresse"""
        if not address:
            return ''

        city_pattern = re.compile(r'\b\d{5}\s+([A-Za-zÀ-ÿ\s\'-]{2,50})\b')
        match = city_pattern.search(address)

        if match:
            return match.group(1).strip().title()

        words = address.split()
        if words:
            last_word = words[-1].strip()
            if len(last_word) > 2 and last_word.isalpha():
                return last_word.title()

        return ''

    def _guess_gender_from_name(self, first_name: str) -> str:
        """Devine le genre basé sur le prénom"""
        if not first_name or len(first_name) < 2:
            return ''

        masculine_names = {
            'jean', 'pierre', 'michel', 'alain', 'philippe', 'daniel', 'patrick', 'bernard',
            'nicolas', 'julien', 'david', 'christophe', 'laurent', 'fabrice', 'stéphane',
            'ahmed', 'mohammed', 'ali', 'hassan', 'youssef', 'karim', 'omar', 'abdou'
        }

        feminine_names = {
            'marie', 'catherine', 'françoise', 'monique', 'isabelle', 'sylvie', 'martine',
            'brigitte', 'sophie', 'nathalie', 'caroline', 'valérie', 'patricia', 'christine',
            'fatima', 'aicha', 'khadija', 'amina', 'sarah', 'leila', 'yasmine', 'sofia'
        }

        name_lower = first_name.lower().strip()

        if name_lower in masculine_names:
            return 'M'
        elif name_lower in feminine_names:
            return 'F'

        if name_lower.endswith(('a', 'e', 'ine', 'elle', 'ette')):
            return 'F'

        return ''

    def _extract_birth_date_from_coordonnees(self, coordonnees: Dict) -> Optional[date]:
        """Extrait la date de naissance des coordonnées"""
        if not coordonnees:
            return None

        date_sources = [
            coordonnees.get('date_naissance', ''),
            coordonnees.get('naissance', ''),
            coordonnees.get('birth_date', ''),
            coordonnees.get('age', '')
        ]

        for source in date_sources:
            if not source:
                continue

            source_str = str(source).strip()

            # Pattern pour date DD/MM/YYYY ou DD-MM-YYYY
            date_pattern = re.compile(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})')
            match = date_pattern.search(source_str)

            if match:
                try:
                    day, month, year = map(int, match.groups())
                    birth_date = date(year, month, day)

                    today = date.today()
                    age = today.year - birth_date.year
                    if 16 <= age <= 80:
                        return birth_date
                except (ValueError, TypeError):
                    continue

            # Pattern pour âge
            age_pattern = re.compile(r'(\d{1,2})\s*(?:ans?)?')
            age_match = age_pattern.search(source_str)

            if age_match:
                try:
                    age = int(age_match.group(1))
                    if 16 <= age <= 80:
                        birth_year = date.today().year - age
                        return date(birth_year, 1, 1)
                except (ValueError, TypeError):
                    continue

        return None

    def _determine_education_level(self, formations: List) -> str:
        """Détermine le niveau d'éducation le plus élevé"""
        if not formations or not isinstance(formations, list):
            return 'Non spécifié'

        levels = []

        for formation in formations:
            if isinstance(formation, dict):
                diplome = str(formation.get('diplome', '')).lower()
                niveau = str(formation.get('niveau', '')).lower()
                domaine = str(formation.get('domaine', '')).lower()

                full_text = f"{diplome} {niveau} {domaine}"

                if any(keyword in full_text for keyword in ['doctorat', 'phd', 'these']):
                    levels.append(8)
                elif any(keyword in full_text for keyword in ['master', 'ingenieur', 'msc', 'diplome ingenieur']):
                    levels.append(5)
                elif any(keyword in full_text for keyword in ['licence', 'bachelor', 'bac+3']):
                    levels.append(3)
                elif any(keyword in full_text for keyword in ['bts', 'dut', 'bac+2']):
                    levels.append(2)
                elif any(keyword in full_text for keyword in ['bac', 'baccalaureat']):
                    levels.append(0)

        if not levels:
            return 'Non spécifié'

        max_level = max(levels)

        level_mapping = {
            0: 'Baccalauréat',
            2: 'Bac+2 (BTS/DUT)',
            3: 'Licence/Bac+3',
            5: 'Master/Ingénieur (Bac+5)',
            8: 'Doctorat (Bac+8+)'
        }

        return level_mapping.get(max_level, 'Formation supérieure')

    def _create_basic_summary(self, cv_data: Dict) -> str:
        """Crée un résumé de base"""
        try:
            titre = cv_data.get('titre_candidat', 'Candidat')
            experience_years = cv_data.get('experience_years', 0)
            formations = cv_data.get('formations', [])
            competences = cv_data.get('competences_techniques', [])

            summary_parts = [f"Profil: {titre}"]

            if experience_years > 0:
                if experience_years == 1:
                    summary_parts.append(f"{experience_years} année d'expérience professionnelle")
                else:
                    summary_parts.append(f"{experience_years} années d'expérience professionnelle")

            if formations:
                summary_parts.append(f"{len(formations)} formation(s)")

            if competences:
                comp_count = min(len(competences), 5)
                summary_parts.append(f"{comp_count} compétences techniques principales")

            return '. '.join(summary_parts) + '.'

        except Exception:
            return 'Résumé automatique non disponible.'

    def _format_ai_summary(self, summary_data: Dict) -> str:
        """Formate le résumé IA en texte lisible"""
        try:
            if 'error' in summary_data:
                return self._create_basic_summary({})

            parts = []

            profil_type = summary_data.get('profil_type', '')
            if profil_type:
                parts.append(f"Profil: {profil_type}")

            exp_prof = summary_data.get('experience_professionnelle', 0)
            niveau_exp = summary_data.get('niveau_experience', '')
            if exp_prof > 0:
                parts.append(f"{exp_prof} années d'expérience ({niveau_exp})")

            formation_years = summary_data.get('formation_academique', 0)
            niveau_formation = summary_data.get('niveau_formation', '')
            if formation_years > 0:
                parts.append(f"Formation: {niveau_formation}")

            domaines = summary_data.get('domaines_expertise', [])
            if domaines:
                parts.append(f"Expertise: {', '.join(domaines[:3])}")

            competences_count = len(summary_data.get('competences_cles', []))
            if competences_count > 0:
                parts.append(f"{competences_count} compétences clés")

            return '. '.join(parts) + '.' if parts else 'Profil polyvalent.'

        except Exception:
            return self._create_basic_summary({})


class CandidateDatabaseManager:
    """
    Gestionnaire pour sauvegarder les candidats en base de données Django
    """

    def __init__(self):
        self.logger = logging.getLogger('CandidateDB')

    @transaction.atomic
    def create_or_update_candidate(self, extracted_data: Dict, cv_data: Dict, cv_file=None, cv_text: str = '') -> Tuple[Candidate, bool]:
        """
        Crée ou met à jour un candidat en base de données
        """
        try:
            # Validation des données obligatoires
            if not extracted_data.get('email') and not (extracted_data.get('first_name') and extracted_data.get('last_name')):
                raise ValidationError("Email OU (Prénom + Nom) requis pour créer un candidat")

            candidate = None
            created = False

            # Recherche par email
            if extracted_data.get('email'):
                try:
                    candidate = Candidate.objects.get(email=extracted_data['email'])
                    self.logger.info(f"Candidat existant trouvé: {candidate.email}")
                except Candidate.DoesNotExist:
                    pass

            # Recherche par nom complet
            if not candidate and extracted_data.get('first_name') and extracted_data.get('last_name'):
                candidates = Candidate.objects.filter(
                    first_name__iexact=extracted_data['first_name'],
                    last_name__iexact=extracted_data['last_name']
                )
                if candidates.exists():
                    candidate = candidates.first()
                    self.logger.info(f"Candidat existant trouvé par nom: {candidate.first_name} {candidate.last_name}")

            # Créer nouveau candidat
            if not candidate:
                candidate = Candidate()
                created = True
                self.logger.info("Création d'un nouveau candidat")
            else:
                self.logger.info("Mise à jour candidat existant")

            # === MISE À JOUR DES CHAMPS ===

            if extracted_data.get('first_name'):
                candidate.first_name = extracted_data['first_name'][:100]
            if extracted_data.get('last_name'):
                candidate.last_name = extracted_data['last_name'][:100]
            if extracted_data.get('email'):
                candidate.email = extracted_data['email'][:254]
            if extracted_data.get('phone'):
                candidate.phone = extracted_data['phone'][:20]
            if extracted_data.get('gender') and extracted_data['gender'] in ['M', 'F']:
                candidate.gender = extracted_data['gender']
            if extracted_data.get('address'):
                candidate.address = extracted_data['address']
            if extracted_data.get('city'):
                candidate.city = extracted_data['city'][:100]
            if extracted_data.get('linkedin_url'):
                candidate.linkedin_url = extracted_data['linkedin_url'][:200]

            if extracted_data.get('birth_date'):
                candidate.birth_date = extracted_data['birth_date']

            if cv_text:
                candidate.cv_text = cv_text

            candidate.cv_parsed_data = cv_data

            if extracted_data.get('skills_extracted'):
                candidate.skills_extracted = extracted_data['skills_extracted']

            if extracted_data.get('experience_years') is not None:
                candidate.experience_years = max(0, int(extracted_data['experience_years']))

            if extracted_data.get('education_level'):
                candidate.education_level = extracted_data['education_level'][:100]

            if extracted_data.get('languages'):
                candidate.languages = extracted_data['languages']

            if extracted_data.get('ai_summary'):
                candidate.ai_summary = extracted_data['ai_summary']

            if cv_file:
                candidate.cv_file = cv_file

            # Validation et sauvegarde
            candidate.full_clean()
            candidate.save()

            self.logger.info(f"✅ Candidat {'créé' if created else 'mis à jour'}: {candidate.first_name} {candidate.last_name}")

            return candidate, created

        except ValidationError as e:
            self.logger.error(f"❌ Erreur validation: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde candidat: {e}")
            raise


class DjangoCVIntegration:
    """
    Classe principale d'intégration CV Parser + Django
    """

    def __init__(self, cv_parser):
        """
        Initialise l'intégration
        """
        self.cv_parser = cv_parser
        self.extractor = CandidateDataExtractor(cv_parser)
        self.db_manager = CandidateDatabaseManager()
        self.logger = logging.getLogger('DjangoCVIntegration')

    def process_cv_file_to_candidate(self, cv_file_path: str, save_to_db: bool = True) -> Dict:
        """
        Traite un fichier CV et crée/met à jour le candidat en base
        """
        try:
            self.logger.info(f"🔍 Traitement CV: {cv_file_path}")

            # 1. Parser le CV
            parsing_result = self.cv_parser.parse_cv_from_pdf(cv_file_path)

            if not parsing_result.success:
                return {
                    'success': False,
                    'error': 'Échec parsing CV',
                    'details': parsing_result.errors,
                    'cv_file': cv_file_path
                }

            cv_data = parsing_result.data
            cv_text = getattr(parsing_result, 'raw_text', '')

            # 2. Extraire les données personnelles
            extracted_data = self.extractor.extract_personal_info_from_cv_data(cv_data)

            result = {
                'success': True,
                'cv_file': cv_file_path,
                'parsing_confidence': parsing_result.confidence,
                'extracted_data': extracted_data,
                'cv_parsed_data': cv_data,
                'candidate': None,
                'created': False
            }

            # 3. Sauvegarder en base si demandé
            if save_to_db:
                try:
                    # Créer un objet fichier Django
                    cv_file_obj = None
                    if cv_file_path:
                        with open(cv_file_path, 'rb') as f:
                            file_content = f.read()
                            file_name = Path(cv_file_path).name
                            cv_file_obj = ContentFile(file_content, name=file_name)

                    candidate, created = self.db_manager.create_or_update_candidate(
                        extracted_data, cv_data, cv_file_obj, cv_text
                    )

                    result['candidate'] = candidate
                    result['created'] = created
                    result['candidate_id'] = candidate.id

                    self.logger.info(f"✅ Candidat {'créé' if created else 'mis à jour'}: {candidate.email}")

                except Exception as db_error:
                    result['db_error'] = str(db_error)
                    self.logger.error(f"❌ Erreur base de données: {db_error}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Erreur traitement CV: {e}")
            return {
                'success': False,
                'error': str(e),
                'cv_file': cv_file_path
            }

    def process_cv_text_to_candidate(self, cv_text: str, filename: str = 'text_direct.txt', save_to_db: bool = True) -> Dict:
        """
        Traite du texte CV directement
        """
        try:
            self.logger.info(f"🔍 Traitement texte CV: {len(cv_text)} caractères")

            # 1. Parser le texte directement
            parsing_result = self.cv_parser.parse_text_directly(cv_text, "cv")

            if not parsing_result.success:
                return {
                    'success': False,
                    'error': 'Échec parsing texte CV',
                    'details': parsing_result.errors,
                    'filename': filename
                }

            cv_data = parsing_result.data

            # 2. Extraire les données personnelles
            extracted_data = self.extractor.extract_personal_info_from_cv_data(cv_data)

            result = {
                'success': True,
                'filename': filename,
                'parsing_confidence': parsing_result.confidence,
                'extracted_data': extracted_data,
                'cv_parsed_data': cv_data,
                'candidate': None,
                'created': False
            }

            # 3. Sauvegarder en base si demandé
            if save_to_db:
                try:
                    candidate, created = self.db_manager.create_or_update_candidate(
                        extracted_data, cv_data, None, cv_text
                    )

                    result['candidate'] = candidate
                    result['created'] = created
                    result['candidate_id'] = candidate.id

                    self.logger.info(f"✅ Candidat {'créé' if created else 'mis à jour'}: {candidate.email}")

                except Exception as db_error:
                    result['db_error'] = str(db_error)
                    self.logger.error(f"❌ Erreur base de données: {db_error}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Erreur traitement texte CV: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }

    def batch_process_cvs_to_candidates(self, cv_directory: str, save_to_db: bool = True) -> Dict:
        """
        Traite un dossier de CVs en lot
        """
        try:
            cv_dir = Path(cv_directory)
            if not cv_dir.exists():
                raise FileNotFoundError(f"Dossier non trouvé: {cv_directory}")

            pdf_files = list(cv_dir.glob("*.pdf"))
            if not pdf_files:
                return {
                    'success': False,
                    'error': 'Aucun fichier PDF trouvé',
                    'directory': cv_directory
                }

            self.logger.info(f"🚀 Traitement en lot: {len(pdf_files)} CVs")

            results = {
                'success': True,
                'total_files': len(pdf_files),
                'processed': 0,
                'created_candidates': 0,
                'updated_candidates': 0,
                'parsing_errors': 0,
                'db_errors': 0,
                'details': []
            }

            for pdf_file in pdf_files:
                try:
                    self.logger.info(f"📄 Traitement: {pdf_file.name}")

                    result = self.process_cv_file_to_candidate(str(pdf_file), save_to_db)
                    results['processed'] += 1

                    file_result = {
                        'filename': pdf_file.name,
                        'success': result['success'],
                        'parsing_confidence': result.get('parsing_confidence', 0),
                        'candidate_name': '',
                        'candidate_email': '',
                        'experience_years': 0,
                        'education_level': ''
                    }

                    if result['success']:
                        extracted = result.get('extracted_data', {})
                        file_result.update({
                            'candidate_name': f"{extracted.get('first_name', '')} {extracted.get('last_name', '')}".strip(),
                            'candidate_email': extracted.get('email', ''),
                            'experience_years': extracted.get('experience_years', 0),
                            'education_level': extracted.get('education_level', ''),
                            'created': result.get('created', False)
                        })

                        if save_to_db:
                            if result.get('created'):
                                results['created_candidates'] += 1
                            else:
                                results['updated_candidates'] += 1

                            if 'candidate_id' in result:
                                file_result['candidate_id'] = result['candidate_id']

                        if 'db_error' in result:
                            results['db_errors'] += 1
                            file_result['db_error'] = result['db_error']
                    else:
                        results['parsing_errors'] += 1
                        file_result['error'] = result.get('error', 'Erreur inconnue')

                    results['details'].append(file_result)

                except Exception as e:
                    results['parsing_errors'] += 1
                    results['details'].append({
                        'filename': pdf_file.name,
                        'success': False,
                        'error': str(e)
                    })
                    self.logger.error(f"❌ Erreur {pdf_file.name}: {e}")

            success_rate = ((results['created_candidates'] + results['updated_candidates']) /
                            results['total_files'] * 100) if results['total_files'] > 0 else 0

            results['success_rate'] = round(success_rate, 1)

            self.logger.info(f"📊 Traitement terminé:")
            self.logger.info(f"   • Fichiers traités: {results['processed']}/{results['total_files']}")
            self.logger.info(f"   • Candidats créés: {results['created_candidates']}")
            self.logger.info(f"   • Candidats mis à jour: {results['updated_candidates']}")
            self.logger.info(f"   • Taux de réussite: {results['success_rate']}%")

            return results

        except Exception as e:
            self.logger.error(f"❌ Erreur traitement en lot: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory': cv_directory
            }


# === FONCTIONS UTILITAIRES ===

def setup_cv_integration_logging():
    """
    Configure le logging pour l'intégration CV
    """
    import logging

    # Configuration du logger principal
    logger = logging.getLogger('cv_integration')
    logger.setLevel(logging.INFO)

    # Handler pour fichier
    file_handler = logging.FileHandler('cv_integration.log')
    file_handler.setLevel(logging.INFO)

    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_cv_integration_instance(cv_parser):
    """
    Factory function pour créer une instance d'intégration
    """
    setup_cv_integration_logging()
    return DjangoCVIntegration(cv_parser)# recruitment/cv_integration.py
"""
Intégration Django CV Parser - Remplissage automatique du modèle Candidate
Adapté pour votre architecture Django ATS_MA
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import transaction
from pathlib import Path

# Import de votre modèle
from .models import Candidate

# Configurez le logger
logger = logging.getLogger('cv_integration')

class CandidateDataExtractor:
    """
    Extracteur spécialisé pour mapper les données CV vers le modèle Candidate Django
    """

    def __init__(self, cv_parser_instance=None):
        """
        Initialise l'extracteur avec une instance de CVParser
        """
        self.cv_parser = cv_parser_instance
        self.logger = logging.getLogger('CandidateExtractor')

        # Patterns de reconnaissance
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+33|0)[1-9](?:[0-9]{8})')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)

    def extract_personal_info_from_cv_data(self, cv_data: Dict) -> Dict:
        """
        Extrait les informations personnelles depuis les données CV parsées
        """
        extracted = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'phone': '',
            'gender': '',
            'birth_date': None,
            'address': '',
            'city': '',
            'linkedin_url': '',
            'experience_years': 0,
            'education_level': '',
            'skills_extracted': [],
            'languages': [],
            'ai_summary': ''
        }

        try:
            # === EXTRACTION NOM/PRÉNOM ===
            titre_candidat = cv_data.get('titre_candidat', '')
            coordonnees = cv_data.get('coordonnees', {})

            if titre_candidat:
                name_parts = self._extract_names_from_title(titre_candidat)
                extracted['first_name'] = name_parts.get('first_name', '')
                extracted['last_name'] = name_parts.get('last_name', '')

            # Compléter depuis les coordonnées si disponibles
            if coordonnees:
                if not extracted['first_name'] and 'prenom' in coordonnees:
                    extracted['first_name'] = str(coordonnees['prenom']).strip()
                if not extracted['last_name'] and 'nom' in coordonnees:
                    extracted['last_name'] = str(coordonnees['nom']).strip()

            # === EXTRACTION EMAIL ===
            email_sources = [
                coordonnees.get('email', ''),
                coordonnees.get('mail', ''),
                str(cv_data.get('email', '')),
                titre_candidat  # Parfois l'email est dans le titre
            ]

            for source in email_sources:
                if source and isinstance(source, str):
                    email_match = self.email_pattern.search(source)
                    if email_match:
                        extracted['email'] = email_match.group().lower()
                        break

            # === EXTRACTION TÉLÉPHONE ===
            phone_sources = [
                coordonnees.get('telephone', ''),
                coordonnees.get('tel', ''),
                coordonnees.get('mobile', ''),
                str(cv_data.get('telephone', ''))
            ]

            for source in phone_sources:
                if source and isinstance(source, str):
                    phone_match = self.phone_pattern.search(source.replace(' ', '').replace('.', '').replace('-', ''))
                    if phone_match:
                        extracted['phone'] = self._format_french_phone(phone_match.group())
                        break

            # === EXTRACTION ADRESSE ===
            address_sources = [
                coordonnees.get('adresse', ''),
                coordonnees.get('address', ''),
                str(cv_data.get('adresse', ''))
            ]

            for source in address_sources:
                if source and isinstance(source, str) and len(source.strip()) > 5:
                    extracted['address'] = source.strip()
                    # Extraire la ville de l'adresse
                    city = self._extract_city_from_address(source)
                    if city:
                        extracted['city'] = city
                    break

            # === EXTRACTION LINKEDIN ===
            linkedin_sources = [
                coordonnees.get('linkedin', ''),
                str(cv_data.get('linkedin', '')),
                str(cv_data.get('profil_linkedin', ''))
            ]

            for source in linkedin_sources:
                if source and isinstance(source, str):
                    linkedin_match = self.linkedin_pattern.search(source)
                    if linkedin_match:
                        linkedin_url = linkedin_match.group()
                        if not linkedin_url.startswith('http'):
                            linkedin_url = 'https://' + linkedin_url
                        extracted['linkedin_url'] = linkedin_url
                        break

            # === EXTRACTION GENRE (OPTIONNEL) ===
            gender = self._guess_gender_from_name(extracted['first_name'])
            if gender:
                extracted['gender'] = gender

            # === EXTRACTION DATE DE NAISSANCE (OPTIONNEL) ===
            birth_date = self._extract_birth_date_from_coordonnees(coordonnees)
            if birth_date:
                extracted['birth_date'] = birth_date

            # === EXTRACTION EXPÉRIENCE ===
            extracted['experience_years'] = cv_data.get('experience_years', 0)

            # === EXTRACTION NIVEAU D'ÉDUCATION ===
            formations = cv_data.get('formations', [])
            education_level = self._determine_education_level(formations)
            extracted['education_level'] = education_level

            # === EXTRACTION COMPÉTENCES ===
            skills = []
            skills_sources = [
                cv_data.get('competences_techniques', []),
                cv_data.get('competences_informatiques', []),
                cv_data.get('soft_skills', [])
            ]

            for source in skills_sources:
                if isinstance(source, list):
                    skills.extend([str(skill).strip() for skill in source if skill])

            # Déduplication et limitation
            extracted['skills_extracted'] = list(dict.fromkeys(skills))[:20]

            # === EXTRACTION LANGUES ===
            langues = cv_data.get('langues', [])
            languages_list = []

            for langue in langues:
                if isinstance(langue, dict):
                    lang_name = langue.get('langue', '')
                    lang_level = langue.get('niveau', '')
                    if lang_name:
                        languages_list.append({
                            'language': lang_name,
                            'level': lang_level
                        })
                elif isinstance(langue, str) and langue.strip():
                    languages_list.append({
                        'language': langue.strip(),
                        'level': 'Non spécifié'
                    })

            extracted['languages'] = languages_list[:10]

            # === GÉNÉRATION RÉSUMÉ IA ===
            if hasattr(self.cv_parser, 'generate_cv_summary'):
                try:
                    summary = self.cv_parser.generate_cv_summary(cv_data)
                    extracted['ai_summary'] = self._format_ai_summary(summary)
                except Exception as e:
                    self.logger.warning(f"Erreur génération résumé IA: {e}")
                    extracted['ai_summary'] = self._create_basic_summary(cv_data)
            else:
                extracted['ai_summary'] = self._create_basic_summary(cv_data)

            return extracted

        except Exception as e:
            self.logger.error(f"Erreur extraction données personnelles: {e}")
            return extracted

    def _extract_names_from_title(self, title: str) -> Dict[str, str]:
        """Extrait prénom et nom depuis le titre candidat"""
        if not title or not isinstance(title, str):
            return {'first_name': '', 'last_name': ''}

        # Nettoyer le titre
        cleaned = re.sub(r'[^\w\s\'-]', ' ', title)
        words = [w.strip() for w in cleaned.split() if w.strip() and len(w) > 1]

        if len(words) == 0:
            return {'first_name': '', 'last_name': ''}
        elif len(words) == 1:
            return {'first_name': words[0].title(), 'last_name': ''}
        elif len(words) == 2:
            return {'first_name': words[0].title(), 'last_name': words[1].upper()}
        else:
            return {
                'first_name': words[0].title(),
                'last_name': ' '.join(words[1:]).upper()
            }

    def _format_french_phone(self, phone: str) -> str:
        """Formate un numéro de téléphone français"""
        digits = re.sub(r'[^\d]', '', phone)

        if digits.startswith('33') and len(digits) == 11:
            digits = '0' + digits[2:]

        if len(digits) == 10 and digits.startswith('0'):
            return f"{digits[:2]}.{digits[2:4]}.{digits[4:6]}.{digits[6:8]}.{digits[8:]}"

        return digits

    def _extract_city_from_address(self, address: str) -> str:
        """Extrait la ville depuis une adresse"""
        if not address:
            return ''

        city_pattern = re.compile(r'\b\d{5}\s+([A-Za-zÀ-ÿ\s\'-]{2,50})\b')
        match = city_pattern.search(address)

        if match:
            return match.group(1).strip().title()

        words = address.split()
        if words:
            last_word = words[-1].strip()
            if len(last_word) > 2 and last_word.isalpha():
                return last_word.title()

        return ''

    def _guess_gender_from_name(self, first_name: str) -> str:
        """Devine le genre basé sur le prénom"""
        if not first_name or len(first_name) < 2:
            return ''

        masculine_names = {
            'jean', 'pierre', 'michel', 'alain', 'philippe', 'daniel', 'patrick', 'bernard',
            'nicolas', 'julien', 'david', 'christophe', 'laurent', 'fabrice', 'stéphane',
            'ahmed', 'mohammed', 'ali', 'hassan', 'youssef', 'karim', 'omar', 'abdou'
        }

        feminine_names = {
            'marie', 'catherine', 'françoise', 'monique', 'isabelle', 'sylvie', 'martine',
            'brigitte', 'sophie', 'nathalie', 'caroline', 'valérie', 'patricia', 'christine',
            'fatima', 'aicha', 'khadija', 'amina', 'sarah', 'leila', 'yasmine', 'sofia'
        }

        name_lower = first_name.lower().strip()

        if name_lower in masculine_names:
            return 'M'
        elif name_lower in feminine_names:
            return 'F'

        if name_lower.endswith(('a', 'e', 'ine', 'elle', 'ette')):
            return 'F'

        return ''

    def _extract_birth_date_from_coordonnees(self, coordonnees: Dict) -> Optional[date]:
        """Extrait la date de naissance des coordonnées"""
        if not coordonnees:
            return None

        date_sources = [
            coordonnees.get('date_naissance', ''),
            coordonnees.get('naissance', ''),
            coordonnees.get('birth_date', ''),
            coordonnees.get('age', '')
        ]

        for source in date_sources:
            if not source:
                continue

            source_str = str(source).strip()

            # Pattern pour date DD/MM/YYYY ou DD-MM-YYYY
            date_pattern = re.compile(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})')
            match = date_pattern.search(source_str)

            if match:
                try:
                    day, month, year = map(int, match.groups())
                    birth_date = date(year, month, day)

                    today = date.today()
                    age = today.year - birth_date.year
                    if 16 <= age <= 80:
                        return birth_date
                except (ValueError, TypeError):
                    continue

            # Pattern pour âge
            age_pattern = re.compile(r'(\d{1,2})\s*(?:ans?)?')
            age_match = age_pattern.search(source_str)

            if age_match:
                try:
                    age = int(age_match.group(1))
                    if 16 <= age <= 80:
                        birth_year = date.today().year - age
                        return date(birth_year, 1, 1)
                except (ValueError, TypeError):
                    continue

        return None

    def _determine_education_level(self, formations: List) -> str:
        """Détermine le niveau d'éducation le plus élevé"""
        if not formations or not isinstance(formations, list):
            return 'Non spécifié'

        levels = []

        for formation in formations:
            if isinstance(formation, dict):
                diplome = str(formation.get('diplome', '')).lower()
                niveau = str(formation.get('niveau', '')).lower()
                domaine = str(formation.get('domaine', '')).lower()

                full_text = f"{diplome} {niveau} {domaine}"

                if any(keyword in full_text for keyword in ['doctorat', 'phd', 'these']):
                    levels.append(8)
                elif any(keyword in full_text for keyword in ['master', 'ingenieur', 'msc', 'diplome ingenieur']):
                    levels.append(5)
                elif any(keyword in full_text for keyword in ['licence', 'bachelor', 'bac+3']):
                    levels.append(3)
                elif any(keyword in full_text for keyword in ['bts', 'dut', 'bac+2']):
                    levels.append(2)
                elif any(keyword in full_text for keyword in ['bac', 'baccalaureat']):
                    levels.append(0)

        if not levels:
            return 'Non spécifié'

        max_level = max(levels)

        level_mapping = {
            0: 'Baccalauréat',
            2: 'Bac+2 (BTS/DUT)',
            3: 'Licence/Bac+3',
            5: 'Master/Ingénieur (Bac+5)',
            8: 'Doctorat (Bac+8+)'
        }

        return level_mapping.get(max_level, 'Formation supérieure')

    def _create_basic_summary(self, cv_data: Dict) -> str:
        """Crée un résumé de base"""
        try:
            titre = cv_data.get('titre_candidat', 'Candidat')
            experience_years = cv_data.get('experience_years', 0)
            formations = cv_data.get('formations', [])
            competences = cv_data.get('competences_techniques', [])

            summary_parts = [f"Profil: {titre}"]

            if experience_years > 0:
                if experience_years == 1:
                    summary_parts.append(f"{experience_years} année d'expérience professionnelle")
                else:
                    summary_parts.append(f"{experience_years} années d'expérience professionnelle")

            if formations:
                summary_parts.append(f"{len(formations)} formation(s)")

            if competences:
                comp_count = min(len(competences), 5)
                summary_parts.append(f"{comp_count} compétences techniques principales")

            return '. '.join(summary_parts) + '.'

        except Exception:
            return 'Résumé automatique non disponible.'

    def _format_ai_summary(self, summary_data: Dict) -> str:
        """Formate le résumé IA en texte lisible"""
        try:
            if 'error' in summary_data:
                return self._create_basic_summary({})

            parts = []

            profil_type = summary_data.get('profil_type', '')
            if profil_type:
                parts.append(f"Profil: {profil_type}")

            exp_prof = summary_data.get('experience_professionnelle', 0)
            niveau_exp = summary_data.get('niveau_experience', '')
            if exp_prof > 0:
                parts.append(f"{exp_prof} années d'expérience ({niveau_exp})")

            formation_years = summary_data.get('formation_academique', 0)
            niveau_formation = summary_data.get('niveau_formation', '')
            if formation_years > 0:
                parts.append(f"Formation: {niveau_formation}")

            domaines = summary_data.get('domaines_expertise', [])
            if domaines:
                parts.append(f"Expertise: {', '.join(domaines[:3])}")

            competences_count = len(summary_data.get('competences_cles', []))
            if competences_count > 0:
                parts.append(f"{competences_count} compétences clés")

            return '. '.join(parts) + '.' if parts else 'Profil polyvalent.'

        except Exception:
            return self._create_basic_summary({})


class CandidateDatabaseManager:
    """
    Gestionnaire pour sauvegarder les candidats en base de données Django
    """

    def __init__(self):
        self.logger = logging.getLogger('CandidateDB')

    @transaction.atomic
    def create_or_update_candidate(self, extracted_data: Dict, cv_data: Dict, cv_file=None, cv_text: str = '') -> Tuple[Candidate, bool]:
        """
        Crée ou met à jour un candidat en base de données
        """
        try:
            # Validation des données obligatoires
            if not extracted_data.get('email') and not (extracted_data.get('first_name') and extracted_data.get('last_name')):
                raise ValidationError("Email OU (Prénom + Nom) requis pour créer un candidat")

            candidate = None
            created = False

            # Recherche par email
            if extracted_data.get('email'):
                try:
                    candidate = Candidate.objects.get(email=extracted_data['email'])
                    self.logger.info(f"Candidat existant trouvé: {candidate.email}")
                except Candidate.DoesNotExist:
                    pass

            # Recherche par nom complet
            if not candidate and extracted_data.get('first_name') and extracted_data.get('last_name'):
                candidates = Candidate.objects.filter(
                    first_name__iexact=extracted_data['first_name'],
                    last_name__iexact=extracted_data['last_name']
                )
                if candidates.exists():
                    candidate = candidates.first()
                    self.logger.info(f"Candidat existant trouvé par nom: {candidate.first_name} {candidate.last_name}")

            # Créer nouveau candidat
            if not candidate:
                candidate = Candidate()
                created = True
                self.logger.info("Création d'un nouveau candidat")
            else:
                self.logger.info("Mise à jour candidat existant")

            # === MISE À JOUR DES CHAMPS ===

            if extracted_data.get('first_name'):
                candidate.first_name = extracted_data['first_name'][:100]
            if extracted_data.get('last_name'):
                candidate.last_name = extracted_data['last_name'][:100]
            if extracted_data.get('email'):
                candidate.email = extracted_data['email'][:254]
            if extracted_data.get('phone'):
                candidate.phone = extracted_data['phone'][:20]
            if extracted_data.get('gender') and extracted_data['gender'] in ['M', 'F']:
                candidate.gender = extracted_data['gender']
            if extracted_data.get('address'):
                candidate.address = extracted_data['address']
            if extracted_data.get('city'):
                candidate.city = extracted_data['city'][:100]
            if extracted_data.get('linkedin_url'):
                candidate.linkedin_url = extracted_data['linkedin_url'][:200]

            if extracted_data.get('birth_date'):
                candidate.birth_date = extracted_data['birth_date']

            if cv_text:
                candidate.cv_text = cv_text

            candidate.cv_parsed_data = cv_data

            if extracted_data.get('skills_extracted'):
                candidate.skills_extracted = extracted_data['skills_extracted']

            if extracted_data.get('experience_years') is not None:
                candidate.experience_years = max(0, int(extracted_data['experience_years']))

            if extracted_data.get('education_level'):
                candidate.education_level = extracted_data['education_level'][:100]

            if extracted_data.get('languages'):
                candidate.languages = extracted_data['languages']

            if extracted_data.get('ai_summary'):
                candidate.ai_summary = extracted_data['ai_summary']

            if cv_file:
                candidate.cv_file = cv_file

            # Validation et sauvegarde
            candidate.full_clean()
            candidate.save()

            self.logger.info(f"✅ Candidat {'créé' if created else 'mis à jour'}: {candidate.first_name} {candidate.last_name}")

            return candidate, created

        except ValidationError as e:
            self.logger.error(f"❌ Erreur validation: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde candidat: {e}")
            raise


class DjangoCVIntegration:
    """
    Classe principale d'intégration CV Parser + Django
    """

    def __init__(self, cv_parser):
        """
        Initialise l'intégration
        """
        self.cv_parser = cv_parser
        self.extractor = CandidateDataExtractor(cv_parser)
        self.db_manager = CandidateDatabaseManager()
        self.logger = logging.getLogger('DjangoCVIntegration')

    def process_cv_file_to_candidate(self, cv_file_path: str, save_to_db: bool = True) -> Dict:
        """
        Traite un fichier CV et crée/met à jour le candidat en base
        """
        try:
            self.logger.info(f"🔍 Traitement CV: {cv_file_path}")

            # 1. Parser le CV
            parsing_result = self.cv_parser.parse_cv_from_pdf(cv_file_path)

            if not parsing_result.success:
                return {
                    'success': False,
                    'error': 'Échec parsing CV',
                    'details': parsing_result.errors,
                    'cv_file': cv_file_path
                }

            cv_data = parsing_result.data
            cv_text = getattr(parsing_result, 'raw_text', '')

            # 2. Extraire les données personnelles
            extracted_data = self.extractor.extract_personal_info_from_cv_data(cv_data)

            result = {
                'success': True,
                'cv_file': cv_file_path,
                'parsing_confidence': parsing_result.confidence,
                'extracted_data': extracted_data,
                'cv_parsed_data': cv_data,
                'candidate': None,
                'created': False
            }

            # 3. Sauvegarder en base si demandé
            if save_to_db:
                try:
                    # Créer un objet fichier Django
                    cv_file_obj = None
                    if cv_file_path:
                        with open(cv_file_path, 'rb') as f:
                            file_content = f.read()
                            file_name = Path(cv_file_path).name
                            cv_file_obj = ContentFile(file_content, name=file_name)

                    candidate, created = self.db_manager.create_or_update_candidate(
                        extracted_data, cv_data, cv_file_obj, cv_text
                    )

                    result['candidate'] = candidate
                    result['created'] = created
                    result['candidate_id'] = candidate.id

                    self.logger.info(f"✅ Candidat {'créé' if created else 'mis à jour'}: {candidate.email}")

                except Exception as db_error:
                    result['db_error'] = str(db_error)
                    self.logger.error(f"❌ Erreur base de données: {db_error}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Erreur traitement CV: {e}")
            return {
                'success': False,
                'error': str(e),
                'cv_file': cv_file_path
            }

    def process_cv_text_to_candidate(self, cv_text: str, filename: str = 'text_direct.txt', save_to_db: bool = True) -> Dict:
        """
        Traite du texte CV directement
        """
        try:
            self.logger.info(f"🔍 Traitement texte CV: {len(cv_text)} caractères")

            # 1. Parser le texte directement
            parsing_result = self.cv_parser.parse_text_directly(cv_text, "cv")

            if not parsing_result.success:
                return {
                    'success': False,
                    'error': 'Échec parsing texte CV',
                    'details': parsing_result.errors,
                    'filename': filename
                }

            cv_data = parsing_result.data

            # 2. Extraire les données personnelles
            extracted_data = self.extractor.extract_personal_info_from_cv_data(cv_data)

            result = {
                'success': True,
                'filename': filename,
                'parsing_confidence': parsing_result.confidence,
                'extracted_data': extracted_data,
                'cv_parsed_data': cv_data,
                'candidate': None,
                'created': False
            }

            # 3. Sauvegarder en base si demandé
            if save_to_db:
                try:
                    candidate, created = self.db_manager.create_or_update_candidate(
                        extracted_data, cv_data, None, cv_text
                    )

                    result['candidate'] = candidate
                    result['created'] = created
                    result['candidate_id'] = candidate.id

                    self.logger.info(f"✅ Candidat {'créé' if created else 'mis à jour'}: {candidate.email}")

                except Exception as db_error:
                    result['db_error'] = str(db_error)
                    self.logger.error(f"❌ Erreur base de données: {db_error}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Erreur traitement texte CV: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }

    def batch_process_cvs_to_candidates(self, cv_directory: str, save_to_db: bool = True) -> Dict:
        """
        Traite un dossier de CVs en lot
        """
        try:
            cv_dir = Path(cv_directory)
            if not cv_dir.exists():
                raise FileNotFoundError(f"Dossier non trouvé: {cv_directory}")

            pdf_files = list(cv_dir.glob("*.pdf"))
            if not pdf_files:
                return {
                    'success': False,
                    'error': 'Aucun fichier PDF trouvé',
                    'directory': cv_directory
                }

            self.logger.info(f"🚀 Traitement en lot: {len(pdf_files)} CVs")

            results = {
                'success': True,
                'total_files': len(pdf_files),
                'processed': 0,
                'created_candidates': 0,
                'updated_candidates': 0,
                'parsing_errors': 0,
                'db_errors': 0,
                'details': []
            }

            for pdf_file in pdf_files:
                try:
                    self.logger.info(f"📄 Traitement: {pdf_file.name}")

                    result = self.process_cv_file_to_candidate(str(pdf_file), save_to_db)
                    results['processed'] += 1

                    file_result = {
                        'filename': pdf_file.name,
                        'success': result['success'],
                        'parsing_confidence': result.get('parsing_confidence', 0),
                        'candidate_name': '',
                        'candidate_email': '',
                        'experience_years': 0,
                        'education_level': ''
                    }

                    if result['success']:
                        extracted = result.get('extracted_data', {})
                        file_result.update({
                            'candidate_name': f"{extracted.get('first_name', '')} {extracted.get('last_name', '')}".strip(),
                            'candidate_email': extracted.get('email', ''),
                            'experience_years': extracted.get('experience_years', 0),
                            'education_level': extracted.get('education_level', ''),
                            'created': result.get('created', False)
                        })

                        if save_to_db:
                            if result.get('created'):
                                results['created_candidates'] += 1
                            else:
                                results['updated_candidates'] += 1

                            if 'candidate_id' in result:
                                file_result['candidate_id'] = result['candidate_id']

                        if 'db_error' in result:
                            results['db_errors'] += 1
                            file_result['db_error'] = result['db_error']
                    else:
                        results['parsing_errors'] += 1
                        file_result['error'] = result.get('error', 'Erreur inconnue')

                    results['details'].append(file_result)

                except Exception as e:
                    results['parsing_errors'] += 1
                    results['details'].append({
                        'filename': pdf_file.name,
                        'success': False,
                        'error': str(e)
                    })
                    self.logger.error(f"❌ Erreur {pdf_file.name}: {e}")

            success_rate = ((results['created_candidates'] + results['updated_candidates']) /
                          results['total_files'] * 100) if results['total_files'] > 0 else 0

            results['success_rate'] = round(success_rate, 1)

            self.logger.info(f"📊 Traitement terminé:")
            self.logger.info(f"   • Fichiers traités: {results['processed']}/{results['total_files']}")
            self.logger.info(f"   • Candidats créés: {results['created_candidates']}")
            self.logger.info(f"   • Candidats mis à jour: {results['updated_candidates']}")
            self.logger.info(f"   • Taux de réussite: {results['success_rate']}%")

            return results

        except Exception as e:
            self.logger.error(f"❌ Erreur traitement en lot: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory': cv_directory
            }


# === FONCTIONS UTILITAIRES ===

def setup_cv_integration_logging():
    """
    Configure le logging pour l'intégration CV
    """
    import logging

    # Configuration du logger principal
    logger = logging.getLogger('cv_integration')
    logger.setLevel(logging.INFO)

    # Handler pour fichier
    file_handler = logging.FileHandler('cv_integration.log')
    file_handler.setLevel(logging.INFO)

    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_cv_integration_instance(cv_parser):
    """
    Factory function pour créer une instance d'intégration
    """
    setup_cv_integration_logging()
    return DjangoCVIntegration(cv_parser)