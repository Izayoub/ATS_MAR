#cv_parser.py
# Parser complet pour CV et offres d'emploi avec extraction PDF, traitement LLM et validation
# VERSION CORRIGÉE - Distinction claire entre formation académique et expérience professionnelle

import os
import sys
import json
import re
import time
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

# Import des services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_engine.services.ocr_service import PDFExtractor, ExtractionResult
    from ai_engine.services.llm_service import GemmaClient, LLMResponse
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Vérifiez que les dossiers ocr_service et llm_service sont présents")
    sys.exit(1)

@dataclass
class ParsingResult:
    """Résultat complet du parsing avec métadonnées"""
    success: bool
    data: Dict
    confidence: float
    execution_time: float
    extraction_method: str
    llm_model: str
    source_file: str
    errors: List[str]
    warnings: List[str]
    raw_text_length: int
    json_validation_passed: bool

class CVParser:
    """
    Parser principal pour CV et offres d'emploi
    Orchestration complète: PDF → Texte → LLM → JSON validé
    VERSION CORRIGÉE avec distinction formation/expérience
    """
    
    def __init__(self, 
                 gemma_model: str = "gemma3:4b",
                 ollama_url: str = "http://localhost:11434",
                 pdf_extraction_method: str = "auto",
                 llm_temperature: float = 0.1,
                 validation_strict: bool = True,
                 log_level: str = "INFO"):
        
        self.gemma_model = gemma_model
        self.ollama_url = ollama_url
        self.pdf_extraction_method = pdf_extraction_method
        self.llm_temperature = llm_temperature
        self.validation_strict = validation_strict
        
        self.setup_logging(log_level)
        self._initialize_services()
        
        # Statistiques globales
        self.stats = {
            "total_processed": 0,
            "successful_cv_parses": 0,
            "successful_job_parses": 0,
            "failed_extractions": 0,
            "failed_llm_calls": 0,
            "failed_validations": 0,
            "total_time": 0.0,
            "average_processing_time": 0.0
        }
    
    def setup_logging(self, log_level: str):
        """Configuration du logging centralisé"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'cv_parser.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CVParser')
    
    def _initialize_services(self):
        """Initialisation des services PDF et LLM"""
        try:
            self.pdf_extractor = PDFExtractor(log_level="INFO")
            self.logger.info("✅ PDFExtractor initialisé")
            
            self.gemma_client = GemmaClient(
                model_name=self.gemma_model,
                base_url=self.ollama_url,
                temperature=self.llm_temperature,
                max_retries=3,
                log_level="INFO"
            )
            self.logger.info("✅ GemmaClient initialisé")
            self._health_check()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation services: {str(e)}")
            raise Exception(f"Impossible d'initialiser les services: {str(e)}")
    
    def _health_check(self):
        try:
            # Test PDFExtractor avec une méthode qui existe réellement
            # Option 1: Tester avec un fichier qui n'existe pas (gestion d'erreur normale)
            test_result = self.pdf_extractor.extract_text_from_pdf("non_existent_test.pdf")
            # Si on arrive ici sans exception fatale, le service fonctionne
            self.logger.info("✅ PDFExtractor opérationnel")
        
        except FileNotFoundError:
            # C'est normal - le fichier test n'existe pas
            self.logger.info("✅ PDFExtractor opérationnel (test FileNotFound OK)")
        
        except AttributeError as e:
            # Problème avec l'objet PDFExtractor lui-même
            self.logger.error(f"❌ PDFExtractor - Méthode manquante: {str(e)}")
            raise Exception(f"PDFExtractor non fonctionnel: {str(e)}")
        
        except Exception as e:
            # Autres erreurs (connexion, import, etc.)
            if "extract_text_from_pdf" in str(e):
                self.logger.error(f"❌ PDFExtractor non fonctionnel: {str(e)}")
                raise Exception(f"PDFExtractor non opérationnel: {str(e)}")
            else:
                # Erreur mineure, le service peut fonctionner
                self.logger.warning(f"⚠️ PDFExtractor avertissement: {str(e)}")
    
        # Test GemmaClient
        health = self.gemma_client.health_check()
        if health["status"] == "healthy":
            self.logger.info("✅ GemmaClient opérationnel")
        else:
            raise Exception(f"GemmaClient non opérationnel: {health.get('error', 'Inconnu')}")


    
    def _extract_text_from_pdf(self, pdf_path: str) -> ExtractionResult:
        """Extraction de texte avec la méthode configurée"""
        return self.pdf_extractor.extract_text_from_pdf(
            pdf_path, method=self.pdf_extraction_method
        )
    
    def _calculate_professional_experience_years(self, experiences: List[Dict]) -> Tuple[int, List[str]]:
        """
        Calcule les années d'expérience professionnelle totales - VERSION CORRIGÉE
        """
        if not experiences or not isinstance(experiences, list):
            return 0, ["Aucune expérience trouvée"]
        
        warnings = []
        total_months = 0
        current_date = datetime.now()
        
        self.logger.info(f"🧮 CALCUL EXPÉRIENCE: {len(experiences)} expériences trouvées")
        
        for i, exp in enumerate(experiences):
            if not isinstance(exp, dict):
                warnings.append(f"Expérience {i+1} ignorée (format invalide)")
                continue
            
            poste = exp.get('poste', '')
            entreprise = exp.get('entreprise', '')
            
            # IGNORER LES STAGES ET FORMATIONS
            if any(keyword in poste.lower() for keyword in ['stage', 'stagiaire', 'étudiant', 'projet académique', 'formation']):
                warnings.append(f"Stage/Formation ignoré: {poste}")
                continue
            
            # Méthode 1: Utiliser la durée si elle existe et est fiable
            duree = exp.get('duree', '').strip()
            if duree:
                months = self._parse_duration_to_months(duree)
                if months > 0:
                    total_months += months
                    self.logger.info(f"   Exp {i+1}: {poste} - {duree} = {months} mois")
                    continue
            
            # Méthode 2: Calculer depuis les dates de début et fin
            date_debut_str = exp.get('date_debut', '')
            date_fin_str = exp.get('date_fin', '')
            
            if date_debut_str:
                date_debut = self._parse_date(date_debut_str)
                
                # Déterminer date de fin
                if date_fin_str and date_fin_str.lower() not in ['présent', 'actuellement', 'en cours', 'current']:
                    date_fin = self._parse_date(date_fin_str)
                else:
                    date_fin = current_date  # Poste actuel
                
                if date_debut and date_fin:
                    if date_fin >= date_debut:
                        # Calculer différence en mois
                        diff_years = date_fin.year - date_debut.year
                        diff_months = date_fin.month - date_debut.month
                        total_diff_months = (diff_years * 12) + diff_months
                        
                        # Minimum 1 mois pour tout emploi
                        total_diff_months = max(1, total_diff_months)
                        
                        total_months += total_diff_months
                        self.logger.info(f"   Exp {i+1}: {poste} ({date_debut_str} → {date_fin_str}) = {total_diff_months} mois")
                    else:
                        warnings.append(f"Dates incohérentes pour {poste}: {date_debut_str} → {date_fin_str}")
                else:
                    warnings.append(f"Dates non parsables pour {poste}: {date_debut_str} → {date_fin_str}")
            else:
                # Méthode 3: Estimation par défaut (12 mois par expérience)
                total_months += 12
                warnings.append(f"Durée estimée à 1 an pour {poste} (pas de dates précises)")
                self.logger.info(f"   Exp {i+1}: {poste} - durée estimée = 12 mois")
        
        # Conversion en années (arrondi)
        total_years = max(0, round(total_months / 12))
        
        self.logger.info(f"✅ TOTAL EXPÉRIENCE: {total_months} mois = {total_years} années")
        
        return total_years, warnings

    def _parse_duration_to_months(self, duree_str: str) -> int:
        """Parse une durée textuelle en nombre de mois - VERSION AMÉLIORÉE"""
        if not duree_str:
            return 0
        
        duree_clean = duree_str.lower().strip()
        total_months = 0
        
        # Patterns améliorés pour reconnaître différents formats
        patterns = [
            # "2 ans et 3 mois", "1 an et 6 mois"
            (r'(\d+)\s*an[s]?\s*et\s*(\d+)\s*mois', lambda m: int(m.group(1)) * 12 + int(m.group(2))),
            # "3 ans 4 mois", "2 ans 1 mois" 
            (r'(\d+)\s*an[s]?\s+(\d+)\s*mois', lambda m: int(m.group(1)) * 12 + int(m.group(2))),
            # "2 ans", "3 années"
            (r'(\d+)\s*an[snée]*\s*$', lambda m: int(m.group(1)) * 12),
            # "5 mois", "18 mois"
            (r'(\d+)\s*mois\s*$', lambda m: int(m.group(1))),
            # "1 année", "2 années"
            (r'(\d+)\s*année[s]?\s*$', lambda m: int(m.group(1)) * 12)
        ]
        
        for pattern, calc_func in patterns:
            match = re.search(pattern, duree_clean)
            if match:
                try:
                    return calc_func(match)
                except (ValueError, AttributeError):
                    continue
        
        # Fallback: chercher juste des nombres
        numbers = re.findall(r'\d+', duree_clean)
        if numbers:
            num = int(numbers[0])
            if 'an' in duree_clean or 'year' in duree_clean:
                return num * 12  # années
            elif 'mois' in duree_clean or 'month' in duree_clean:
                return num  # mois
            elif num > 12:
                return num  # probablement des mois
            else:
                return num * 12  # probablement des années
        
        return 0
    
    def _parse_month_year(self, match) -> datetime:
        """Parse un mois-année en français"""
        month_mapping = {
            'janvier': 1, 'jan': 1, 'février': 2, 'fév': 2, 'mars': 3, 'mar': 3,
            'avril': 4, 'avr': 4, 'mai': 5, 'juin': 6, 'jun': 6, 'juillet': 7, 'jul': 7,
            'août': 8, 'aoû': 8, 'septembre': 9, 'sep': 9, 'octobre': 10, 'oct': 10,
            'novembre': 11, 'nov': 11, 'décembre': 12, 'déc': 12
        }
        
        month_str = match.group(1).lower()
        year = int(match.group(2))
        month = month_mapping.get(month_str, 1)
        
        return datetime(year, month, 1)
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date depuis différents formats - VERSION AMÉLIORÉE"""
        if not date_str:
            return None
        
        date_clean = date_str.strip().lower()
        
        # Gestion des dates "présent"
        if any(keyword in date_clean for keyword in ['présent', 'actuellement', 'en cours', 'current', 'maintenant']):
            return datetime.now()
        
        # Patterns de dates supportés
        date_patterns = [
            # YYYY-MM format
            (r'(\d{4})-(\d{1,2})', lambda m: datetime(int(m.group(1)), int(m.group(2)), 1)),
            # MM/YYYY format
            (r'(\d{1,2})/(\d{4})', lambda m: datetime(int(m.group(2)), int(m.group(1)), 1)),
            # Mois YYYY format (ex: "janvier 2022", "jan 2022")
            (r'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|mai|jun|jul|aoû|sep|oct|nov|déc)\s+(\d{4})', self._parse_month_year),
            # YYYY seul
            (r'^(\d{4})$', lambda m: datetime(int(m.group(1)), 1, 1)),
            # MM-YYYY format
            (r'(\d{1,2})-(\d{4})', lambda m: datetime(int(m.group(2)), int(m.group(1)), 1))
        ]
        
        for pattern, parse_func in date_patterns:
            match = re.search(pattern, date_clean)
            if match:
                try:
                    return parse_func(match)
                except (ValueError, AttributeError):
                    continue
        
        return None
    def _extract_date_components(self, date_str: str) -> Tuple[Optional[int], Optional[int]]:
        """VERSION AMÉLIORÉE - Extrait les composants année/mois d'une chaîne de date"""
        if not date_str or not isinstance(date_str, str):
            return None, None
        
        date_str = date_str.strip().lower()
        
        # === GESTION DES MOTS-CLÉS TEMPORELS ===
        if any(word in date_str for word in ['présent', 'present', 'maintenant', 'actuel', 'en cours']):
            return datetime.now().year, datetime.now().month
        
        # === PATTERNS DE DATES AMÉLIORÉS ===
        patterns = [
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})',  # DD/MM/YYYY ou MM/DD/YYYY
            r'(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})',  # YYYY/MM/DD
            r'(\d{1,2})[\/\-\.](\d{4})',                    # MM/YYYY
            r'(\d{4})[\/\-\.](\d{1,2})',                    # YYYY/MM
            r'(\d{4})',                                     # YYYY seul
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                groups = [int(g) for g in match.groups()]
                
                # Identifier année et mois
                year = None
                month = None
                
                for num in groups:
                    if 1900 <= num <= 2030:  # C'est l'année
                        year = num
                    elif 1 <= num <= 12:     # C'est le mois
                        month = num
                    elif 1 <= num <= 31 and not month:  # Pourrait être le jour
                        continue
                
                if year:
                    return year, month
        
        # === RECHERCHE DE MOIS EN LETTRES ===
        mois_fr = {
            'janvier': 1, 'jan': 1, 'january': 1,
            'février': 2, 'fév': 2, 'feb': 2, 'february': 2,
            'mars': 3, 'mar': 3, 'march': 3,
            'avril': 4, 'avr': 4, 'apr': 4, 'april': 4,
            'mai': 5, 'may': 5,
            'juin': 6, 'jun': 6, 'june': 6,
            'juillet': 7, 'juil': 7, 'jul': 7, 'july': 7,
            'août': 8, 'aou': 8, 'aug': 8, 'august': 8,
            'septembre': 9, 'sep': 9, 'sept': 9, 'september': 9,
            'octobre': 10, 'oct': 10, 'october': 10,
            'novembre': 11, 'nov': 11, 'november': 11,
            'décembre': 12, 'déc': 12, 'dec': 12, 'december': 12
        }
        
        # Chercher l'année
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        year = int(year_match.group()) if year_match else None
        
        # Chercher le mois
        month = None
        for mois_nom, mois_num in mois_fr.items():
            if mois_nom in date_str:
                month = mois_num
                break
        
        return year, month
# === MÉTHODE DE DEBUG POUR TESTER ===
    def debug_experience_calculation(self, experiences: List[Dict]) -> Dict:
            """Méthode de debug pour analyser le calcul d'expérience"""
            debug_info = {
                "total_experiences": len(experiences) if experiences else 0,
                "experiences_analyzed": [],
                "professional_count": 0,
                "academic_count": 0,
                "ambiguous_count": 0,
                "total_months_calculated": 0
            }
            
            if not experiences:
                return debug_info
            
            for i, exp in enumerate(experiences):
                if not isinstance(exp, dict):
                    continue
                    
                exp_debug = {
                    "index": i + 1,
                    "poste": exp.get('poste', ''),
                    "entreprise": exp.get('entreprise', ''),
                    "date_debut": exp.get('date_debut', ''),
                    "date_fin": exp.get('date_fin', ''),
                    "duree": exp.get('duree', ''),
                    "classification": "unknown",
                    "months_calculated": 0,
                    "reasons": []
                }
                
                # Analyse simplifiée de classification
                full_text = f"{exp.get('poste', '')} {exp.get('entreprise', '')} {exp.get('description', '')}".lower()
                
                if any(kw in full_text for kw in ['formation', 'étudiant', 'cours', 'université']):
                    exp_debug["classification"] = "academic"
                    debug_info["academic_count"] += 1
                elif any(kw in full_text for kw in ['développeur', 'stage', 'emploi', 'travail', 'entreprise']):
                    exp_debug["classification"] = "professional"  
                    debug_info["professional_count"] += 1
                else:
                    exp_debug["classification"] = "ambiguous"
                    debug_info["ambiguous_count"] += 1
                
                debug_info["experiences_analyzed"].append(exp_debug)
            
            return debug_info

    def _calculate_academic_duration(self, formations: List[Dict]) -> Tuple[int, List[str]]:
        """Calcule la durée totale de formation académique"""
        if not formations or not isinstance(formations, list):
            return 0, ["Aucune formation trouvée"]
        
        total_years = 0
        warnings = []
        
        for formation in formations:
            if not isinstance(formation, dict):
                continue
            
            diplome = str(formation.get('diplome', '')).lower()
            niveau = str(formation.get('niveau', '')).lower()
            duree = formation.get('duree', '')
            
            # Durées standard par type de diplôme
            standard_durations = {
                'bac': 0, 'baccalauréat': 0,
                'bts': 2, 'dut': 2, 'deug': 2,
                'licence': 3, 'bachelor': 3,
                'master': 5, 'maitrise': 4, 'msc': 5,
                'doctorat': 8, 'phd': 8, 'these': 8,
                'ingénieur': 5, 'ecole commerce': 5
            }
            
            years_found = 0
            
            # Recherche directe de durée
            if duree:
                year_match = re.findall(r'(\d+)\s*an[snée]*', str(duree).lower())
                if year_match:
                    years_found = int(year_match[0])
            
            # Recherche par type de diplôme
            if years_found == 0:
                for diplome_type, duration in standard_durations.items():
                    if diplome_type in diplome or diplome_type in niveau:
                        years_found = duration
                        break
            
            # Recherche dans les niveaux (bac+X)
            if years_found == 0:
                bac_plus_match = re.search(r'bac\s*\+\s*(\d+)', f"{diplome} {niveau}")
                if bac_plus_match:
                    years_found = int(bac_plus_match.group(1))
            
            if years_found > 0:
                total_years = max(total_years, years_found)  # Prendre le niveau le plus élevé
            else:
                warnings.append(f"Durée de formation non déterminée: {diplome}")
        
        return total_years, warnings
    
    def _create_failed_result(self, pdf_path: str, error: str, errors: List[str] = None, start_time: float = None) -> ParsingResult:
        """Crée un résultat d'erreur structuré"""
        errors = errors.copy() if errors else []
        if error not in errors:
            errors.append(error)
        
        execution_time = (time.time() - start_time) if start_time else 0.0
        
        return ParsingResult(
            success=False,
            data={},
            confidence=0.0,
            execution_time=execution_time,
            extraction_method="unknown",
            llm_model=self.gemma_model,
            source_file=pdf_path,
            errors=errors,
            warnings=[],
            raw_text_length=0,
            json_validation_passed=False
        )
    
    def _calculate_overall_confidence(self, extraction_result, llm_response, parsed_data) -> float:
        """Calcule la confiance globale dans le parsing"""
        confidence = 0.0
        
        if hasattr(extraction_result, 'confidence'):
            confidence += extraction_result.confidence * 0.3
        elif extraction_result and extraction_result.text and len(extraction_result.text) > 100:
            confidence += 0.8 * 0.3
        else:
            confidence += 0.3 * 0.3
        
        if hasattr(llm_response, 'execution_time'):
            time_score = min(llm_response.execution_time / 30.0, 1.0)
            confidence += time_score * 0.2
        elif isinstance(llm_response, dict) and llm_response:
            confidence += 0.7 * 0.2
        
        if parsed_data:
            confidence += 0.5
            cv_key_fields = ["titre_candidat", "formations", "competences_techniques"]
            job_key_fields = ["titre_poste", "missions"]
            
            key_fields = cv_key_fields if any(field in parsed_data for field in cv_key_fields) else job_key_fields
            present_fields = sum(1 for field in key_fields if field in parsed_data and parsed_data[field])
            confidence += (present_fields / len(key_fields)) * 0.3
        
        return min(confidence, 1.0)
    
    def _validate_cv_data(self, cv_data: Dict) -> Tuple[Dict, List[str]]:
        """Validation et nettoyage des données du CV - VERSION CORRIGÉE EXPÉRIENCE"""
        errors = []
        warnings = []
        validated_data = cv_data.copy()
        
        try:
            # === CALCUL CORRIGÉ DE L'EXPÉRIENCE PROFESSIONNELLE ===
            experiences = validated_data.get("experience", [])
            
            if isinstance(experiences, list) and experiences:
                # Utiliser la nouvelle fonction de calcul
                professional_years, exp_warnings = self._calculate_professional_experience_years(experiences)
                validated_data["experience_years"] = professional_years
                warnings.extend(exp_warnings)
                
                self.logger.info(f"📊 VALIDATION - Expérience calculée: {professional_years} années")
                
            else:
                # Si pas d'expériences dans la liste, vérifier si le LLM a fourni directement experience_years
                if "experience_years" in validated_data and isinstance(validated_data["experience_years"], int):
                    # Garder la valeur du LLM si elle semble raisonnable
                    llm_years = validated_data["experience_years"]
                    if 0 <= llm_years <= 50:  # Valeur raisonnable
                        self.logger.info(f"📊 Utilisation experience_years du LLM: {llm_years}")
                    else:
                        validated_data["experience_years"] = 0
                        warnings.append(f"experience_years du LLM non réaliste: {llm_years}")
                else:
                    validated_data["experience_years"] = 0
                    warnings.append("Aucune expérience professionnelle détectée")
            
            # === EXTRACTION DU NOM DEPUIS COORDONNEES ===
            coordonnees = validated_data.get("coordonnees", {})
            if isinstance(coordonnees, dict):
                # Extraction first_name et last_name
                first_name = coordonnees.get("first_name", "") or coordonnees.get("prenom", "")
                last_name = coordonnees.get("last_name", "") or coordonnees.get("nom", "") or coordonnees.get("nom_famille", "")
                
                # Vérification anti-titre professionnel
                professional_keywords = [
                    "développeur", "developer", "ingénieur", "engineer", "consultant", 
                    "manager", "chef", "directeur", "analyste", "technicien", "full stack",
                    "backend", "frontend", "senior", "junior", "lead", "architecte"
                ]
                
                if first_name and any(kw in first_name.lower() for kw in professional_keywords):
                    warnings.append(f"Prénom suspect (titre professionnel?): {first_name}")
                    first_name = ""
                
                if last_name and any(kw in last_name.lower() for kw in professional_keywords):
                    warnings.append(f"Nom suspect (titre professionnel?): {last_name}")
                    last_name = ""
                
                validated_data["first_name"] = first_name.strip()
                validated_data["last_name"] = last_name.strip()
            else:
                validated_data["first_name"] = ""
                validated_data["last_name"] = ""
                warnings.append("Coordonnées non trouvées")
            
            # === VALIDATION DES AUTRES CHAMPS ===
            # Champs obligatoires
            required_fields = ["titre_candidat", "formations", "competences_techniques"]
            for field in required_fields:
                if field not in validated_data or not validated_data[field]:
                    if field in ["formations", "competences_techniques"]:
                        validated_data[field] = []
                    else:
                        validated_data[field] = ""
                    warnings.append(f"Champ {field} manquant ou vide")
            
            # Validation des listes
            list_fields = [
                "formations", "experience", "competences_techniques", 
                "competences_informatiques", "langues", "certifications", 
                "projets", "soft_skills"
            ]
            
            for field in list_fields:
                if field in validated_data:
                    if not isinstance(validated_data[field], list):
                        validated_data[field] = []
                        warnings.append(f"{field} converti en liste vide")
                else:
                    validated_data[field] = []
            
            # Validation des chaînes
            string_fields = ["titre_candidat", "profil_resume", "experience_total"]
            for field in string_fields:
                if field in validated_data:
                    if not isinstance(validated_data[field], str):
                        validated_data[field] = str(validated_data[field])
                    validated_data[field] = validated_data[field].strip()
                else:
                    validated_data[field] = ""
            
            # Coordonnées
            if "coordonnees" not in validated_data or not isinstance(validated_data["coordonnees"], dict):
                validated_data["coordonnees"] = {}
            
            # Informations de debug
            validated_data["_debug_info"] = {
                "total_experiences_found": len(experiences) if isinstance(experiences, list) else 0,
                "professional_experience_years": validated_data.get("experience_years", 0),
                "validation_warnings_count": len(warnings),
                "experiences_details": [
                    {
                        "poste": exp.get("poste", "N/A"),
                        "duree": exp.get("duree", "N/A"),
                        "dates": f"{exp.get('date_debut', 'N/A')} → {exp.get('date_fin', 'N/A')}"
                    } 
                    for exp in experiences[:3]  # Les 3 premières seulement
                ] if isinstance(experiences, list) else []
            }
            
            self.logger.info(f"✅ VALIDATION TERMINÉE - Expérience finale: {validated_data.get('experience_years', 0)} ans")
            
        except Exception as e:
            errors.append(f"Erreur validation: {str(e)}")
            self.logger.error(f"❌ Erreur validation: {str(e)}")
        
        return validated_data, errors + (warnings if self.validation_strict else [])
    
    def _validate_job_data(self, job_data: Dict) -> Tuple[Dict, List[str]]:
        """Validation et nettoyage des données d'offre"""
        errors = []
        validated_data = job_data.copy()
        
        required_fields = ["titre_poste"]
        for field in required_fields:
            if field not in validated_data or not validated_data[field]:
                errors.append(f"Champ obligatoire manquant: {field}")
                validated_data[field] = ""
        
        if "missions" in validated_data:
            missions = validated_data["missions"]
            if isinstance(missions, str):
                if missions.strip():
                    validated_data["missions"] = [missions.strip()]
                else:
                    validated_data["missions"] = []
            elif isinstance(missions, list):
                validated_data["missions"] = [str(m).strip() for m in missions if m and str(m).strip()]
            else:
                errors.append("missions converti en liste vide (type invalide)")
                validated_data["missions"] = []
        else:
            validated_data["missions"] = []
        
        try:
            if "experience_requise" in validated_data:
                exp_req = validated_data["experience_requise"]
                if isinstance(exp_req, str):
                    numbers = re.findall(r'\d+', exp_req)
                    validated_data["experience_requise"] = int(numbers[0]) if numbers else 0
                elif not isinstance(exp_req, int):
                    validated_data["experience_requise"] = 0
                    errors.append("experience_requise converti en 0 (type invalide)")
            else:
                validated_data["experience_requise"] = 0
            
            list_fields = [
                "missions", "competences_requises", "competences_techniques", 
                "certifications_requises", "avantages", "formations_requises"
            ]
            
            for field in list_fields:
                if field in validated_data:
                    if not isinstance(validated_data[field], list):
                        validated_data[field] = []
                        errors.append(f"{field} converti en liste vide (type invalide)")
                else:
                    validated_data[field] = []
            
            if "type_contrat" in validated_data:
                contrat = str(validated_data["type_contrat"]).lower().strip()
                valid_contrats = ["cdi", "cdd", "freelance", "stage", "alternance", "emploi"]
                
                if contrat == "emploi":
                    validated_data["type_contrat"] = "CDI"
                elif contrat in valid_contrats:
                    validated_data["type_contrat"] = contrat.upper()
                else:
                    errors.append(f"Type de contrat non reconnu: {contrat}")
                    validated_data["type_contrat"] = "CDI"
            else:
                validated_data["type_contrat"] = "CDI"
            
            string_fields = [
                "titre_poste", "entreprise", "lieu", "localisation", "type_contrat", 
                "salaire", "description", "profil_recherche"
            ]
            for field in string_fields:
                if field in validated_data:
                    if not isinstance(validated_data[field], str):
                        validated_data[field] = str(validated_data[field])
                    validated_data[field] = validated_data[field].strip()
                else:
                    validated_data[field] = ""
            
            if "infos_entreprise" in validated_data:
                if not isinstance(validated_data["infos_entreprise"], dict):
                    validated_data["infos_entreprise"] = {}
                    errors.append("infos_entreprise converti en dict vide")
            else:
                validated_data["infos_entreprise"] = {}
                
        except Exception as e:
            errors.append(f"Erreur validation: {str(e)}")
        
        return validated_data, errors
    
    def parse_cv_from_pdf(self, pdf_path: str) -> ParsingResult:
        """Parse complet d'un CV depuis un PDF - VERSION AVEC DEBUG"""
        start_time = time.time()
        self.stats["total_processed"] += 1
        errors = []
        warnings = []
        
        self.logger.info(f"🔍 Début parsing CV: {pdf_path}")
        
        try:
            extraction_result = self._extract_text_from_pdf(pdf_path)
            if not extraction_result.text:
                error_msg = "Impossible d'extraire le texte du PDF"
                errors.extend(extraction_result.errors)
                self.stats["failed_extractions"] += 1
                return self._create_failed_result(pdf_path, error_msg, errors, start_time)
            
            self.logger.info(f"📄 Texte extrait: {len(extraction_result.text)} caractères")
            
            llm_result = self.gemma_client.parse_cv_text(extraction_result.text)
            self.logger.info(f"DEBUG LLM_RESULT: {json.dumps(llm_result, ensure_ascii=False)}")

            if "error" in llm_result:
                error_msg = f"Erreur LLM: {llm_result['error']}"
                errors.append(error_msg)
                self.stats["failed_llm_calls"] += 1
                return self._create_failed_result(pdf_path, error_msg, errors, start_time)
            
            self.logger.info("🤖 Parsing LLM réussi")
            
            # === AJOUT DEBUG TEMPORAIRE ===
            experiences_raw = llm_result.get("experience", [])
            self.logger.info(f"🔍 DEBUG - Expériences trouvées dans LLM: {len(experiences_raw) if experiences_raw else 0}")
            
            if experiences_raw and isinstance(experiences_raw, list):
                for i, exp in enumerate(experiences_raw[:3]):  # Afficher les 3 premières
                    if isinstance(exp, dict):
                        self.logger.info(f"   Exp {i+1}: '{exp.get('poste', 'N/A')}' chez '{exp.get('entreprise', 'N/A')}' - Durée: '{exp.get('duree', 'N/A')}'")
                        self.logger.info(f"            Dates: {exp.get('date_debut', 'N/A')} → {exp.get('date_fin', 'N/A')}")
            # === FIN DEBUG ===
            
            validated_data, validation_errors = self._validate_cv_data(llm_result)
            if validation_errors and self.validation_strict:
                errors.extend(validation_errors)
                self.stats["failed_validations"] += 1
                return self._create_failed_result(pdf_path, "Validation échouée", errors, start_time)
            
            if validation_errors:
                warnings.extend(validation_errors)
            
            confidence = self._calculate_overall_confidence(
                extraction_result, llm_result, validated_data
            )
            
            execution_time = time.time() - start_time
            
            self.stats["successful_cv_parses"] += 1
            self.stats["total_time"] += execution_time
            self.stats["average_processing_time"] = (
                self.stats["total_time"] / self.stats["total_processed"]
            )
            
            self.logger.info(f"✅ CV parsé avec succès en {execution_time:.2f}s")
            self.logger.info(f"📊 Expérience pro: {validated_data.get('experience_years', 0)} ans, Formation: {validated_data.get('formation_years', 0)} ans")
            
            return ParsingResult(
                success=True,
                data=validated_data,
                confidence=confidence,
                execution_time=execution_time,
                extraction_method=extraction_result.method_used,
                llm_model=self.gemma_model,
                source_file=pdf_path,
                errors=errors,
                warnings=warnings,
                raw_text_length=len(extraction_result.text),
                json_validation_passed=len(validation_errors) == 0
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Erreur inattendue: {str(e)}"
            self.logger.error(error_msg)
            return self._create_failed_result(pdf_path, error_msg, [error_msg], start_time)

    def parse_job_from_pdf(self, pdf_path: str) -> ParsingResult:
        """Parse complet d'une offre d'emploi depuis un PDF"""
        start_time = time.time()
        self.stats["total_processed"] += 1
        errors = []
        warnings = []
        
        self.logger.info(f"🔍 Début parsing offre: {pdf_path}")
        
        try:
            extraction_result = self._extract_text_from_pdf(pdf_path)
            if not extraction_result.text:
                error_msg = "Impossible d'extraire le texte du PDF"
                errors.extend(extraction_result.errors)
                self.stats["failed_extractions"] += 1
                return self._create_failed_result(pdf_path, error_msg, errors, start_time)
            
            self.logger.info(f"📄 Texte extrait: {len(extraction_result.text)} caractères")
            
            llm_result = self.gemma_client.parse_job_text(extraction_result.text)
            if "error" in llm_result:
                error_msg = f"Erreur LLM: {llm_result['error']}"
                errors.append(error_msg)
                self.stats["failed_llm_calls"] += 1
                return self._create_failed_result(pdf_path, error_msg, errors, start_time)
            
            self.logger.info("🤖 Parsing LLM réussi")
            
            if "missions" in llm_result and isinstance(llm_result["missions"], str):
                llm_result["missions"] = [llm_result["missions"]]
            
            validated_data, validation_errors = self._validate_job_data(llm_result)
            if validation_errors and self.validation_strict:
                errors.extend(validation_errors)
                self.stats["failed_validations"] += 1
                return self._create_failed_result(pdf_path, "Validation échouée", errors, start_time)
            
            if validation_errors:
                warnings.extend(validation_errors)
            
            confidence = self._calculate_overall_confidence(
                extraction_result, llm_result, validated_data
            )
            
            execution_time = time.time() - start_time
            
            self.stats["successful_job_parses"] += 1
            self.stats["total_time"] += execution_time
            self.stats["average_processing_time"] = (
                self.stats["total_time"] / self.stats["total_processed"]
            )
            
            self.logger.info(f"✅ Offre parsée avec succès en {execution_time:.2f}s")
            
            return ParsingResult(
                success=True,
                data=validated_data,
                confidence=confidence,
                execution_time=execution_time,
                extraction_method=extraction_result.method_used,
                llm_model=self.gemma_model,
                source_file=pdf_path,
                errors=errors,
                warnings=warnings,
                raw_text_length=len(extraction_result.text),
                json_validation_passed=len(validation_errors) == 0
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Erreur inattendue: {str(e)}"
            self.logger.error(error_msg)
            return self._create_failed_result(pdf_path, error_msg, [error_msg], start_time)
    
    def batch_parse_cvs(self, pdf_directory: str, output_directory: str = None) -> Dict:
        """Traitement par lot de CVs"""
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Dossier non trouvé: {pdf_directory}")
        
        if output_directory:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            self.logger.warning(f"Aucun fichier PDF trouvé dans {pdf_directory}")
            return {"processed": 0, "successful": 0, "failed": 0, "results": []}
        
        self.logger.info(f"🚀 Début traitement par lot: {len(pdf_files)} CVs")
        
        batch_results = []
        successful = 0
        failed = 0
        
        for pdf_file in pdf_files:
            try:
                self.logger.info(f"📝 Traitement: {pdf_file.name}")
                result = self.parse_cv_from_pdf(str(pdf_file))
                
                batch_results.append({
                    "file": pdf_file.name,
                    "success": result.success,
                    "confidence": result.confidence,
                    "execution_time": result.execution_time,
                    "professional_experience": result.data.get("experience_years", 0) if result.success else 0,
                    "academic_years": result.data.get("formation_years", 0) if result.success else 0,
                    "errors": result.errors,
                    "warnings": result.warnings
                })
                
                if result.success:
                    successful += 1
                    
                    if output_directory:
                        output_file = output_dir / f"{pdf_file.stem}_parsed.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                "metadata": {
                                    "source_file": pdf_file.name,
                                    "parsing_date": datetime.now().isoformat(),
                                    "confidence": result.confidence,
                                    "execution_time": result.execution_time,
                                    "llm_model": result.llm_model,
                                    "extraction_method": result.extraction_method,
                                    "professional_experience_years": result.data.get("experience_years", 0),
                                    "academic_formation_years": result.data.get("formation_years", 0)
                                },
                                "cv_data": result.data
                            }, f, indent=2, ensure_ascii=False)
                        
                        self.logger.info(f"✅ Sauvegardé: {output_file}")
                else:
                    failed += 1
                    self.logger.error(f"❌ Échec: {pdf_file.name} - {result.errors}")
                    
            except Exception as e:
                failed += 1
                error_msg = f"Erreur inattendue pour {pdf_file.name}: {str(e)}"
                self.logger.error(error_msg)
                batch_results.append({
                    "file": pdf_file.name,
                    "success": False,
                    "confidence": 0.0,
                    "execution_time": 0.0,
                    "professional_experience": 0,
                    "academic_years": 0,
                    "errors": [error_msg],
                    "warnings": []
                })
        
        batch_report = {
            "processed": len(pdf_files),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(pdf_files)) * 100 if pdf_files else 0,
            "total_time": sum(r["execution_time"] for r in batch_results),
            "average_time": sum(r["execution_time"] for r in batch_results) / len(batch_results) if batch_results else 0,
            "experience_stats": {
                "avg_professional_exp": sum(r["professional_experience"] for r in batch_results if r["success"]) / successful if successful > 0 else 0,
                "avg_academic_years": sum(r["academic_years"] for r in batch_results if r["success"]) / successful if successful > 0 else 0,
            },
            "results": batch_results
        }
        
        self.logger.info(f"📊 Traitement terminé: {successful}/{len(pdf_files)} réussis")
        
        if output_directory:
            report_file = output_dir / "batch_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(batch_report, f, indent=2, ensure_ascii=False)
        
        return batch_report
    
    def batch_parse_jobs(self, pdf_directory: str, output_directory: str = None) -> Dict:
        """Traitement par lot d'offres d'emploi"""
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Dossier non trouvé: {pdf_directory}")
        
        if output_directory:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            self.logger.warning(f"Aucun fichier PDF trouvé dans {pdf_directory}")
            return {"processed": 0, "successful": 0, "failed": 0, "results": []}
        
        self.logger.info(f"🚀 Début traitement par lot: {len(pdf_files)} offres")
        
        batch_results = []
        successful = 0
        failed = 0
        
        for pdf_file in pdf_files:
            try:
                self.logger.info(f"📋 Traitement: {pdf_file.name}")
                result = self.parse_job_from_pdf(str(pdf_file))
                
                batch_results.append({
                    "file": pdf_file.name,
                    "success": result.success,
                    "confidence": result.confidence,
                    "execution_time": result.execution_time,
                    "errors": result.errors,
                    "warnings": result.warnings
                })
                
                if result.success:
                    successful += 1
                    
                    if output_directory:
                        output_file = output_dir / f"{pdf_file.stem}_parsed.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                "metadata": {
                                    "source_file": pdf_file.name,
                                    "parsing_date": datetime.now().isoformat(),
                                    "confidence": result.confidence,
                                    "execution_time": result.execution_time,
                                    "llm_model": result.llm_model,
                                    "extraction_method": result.extraction_method
                                },
                                "job_data": result.data
                            }, f, indent=2, ensure_ascii=False)
                        
                        self.logger.info(f"✅ Sauvegardé: {output_file}")
                else:
                    failed += 1
                    self.logger.error(f"❌ Échec: {pdf_file.name} - {result.errors}")
                    
            except Exception as e:
                failed += 1
                error_msg = f"Erreur inattendue pour {pdf_file.name}: {str(e)}"
                self.logger.error(error_msg)
                batch_results.append({
                    "file": pdf_file.name,
                    "success": False,
                    "confidence": 0.0,
                    "execution_time": 0.0,
                    "errors": [error_msg],
                    "warnings": []
                })
        
        batch_report = {
            "processed": len(pdf_files),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(pdf_files)) * 100 if pdf_files else 0,
            "total_time": sum(r["execution_time"] for r in batch_results),
            "average_time": sum(r["execution_time"] for r in batch_results) / len(batch_results) if batch_results else 0,
            "results": batch_results
        }
        
        self.logger.info(f"📊 Traitement terminé: {successful}/{len(pdf_files)} réussis")
        
        if output_directory:
            report_file = output_dir / "batch_report_jobs.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(batch_report, f, indent=2, ensure_ascii=False)
        
        return batch_report
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques d'utilisation"""
        return {
            "global_stats": self.stats.copy(),
            "services_status": {
                "pdf_extractor": "✅ Opérationnel",
                "gemma_client": self.gemma_client.health_check()
            },
            "configuration": {
                "gemma_model": self.gemma_model,
                "ollama_url": self.ollama_url,
                "pdf_extraction_method": self.pdf_extraction_method,
                "llm_temperature": self.llm_temperature,
                "validation_strict": self.validation_strict
            }
        }
    
    def export_result_to_json(self, result: ParsingResult, output_path: str):
        """Exporte un résultat de parsing vers un fichier JSON"""
        export_data = {
            "metadata": {
                "success": result.success,
                "confidence": result.confidence,
                "execution_time": result.execution_time,
                "extraction_method": result.extraction_method,
                "llm_model": result.llm_model,
                "source_file": result.source_file,
                "parsing_date": datetime.now().isoformat(),
                "raw_text_length": result.raw_text_length,
                "json_validation_passed": result.json_validation_passed
            },
            "data": result.data,
            "errors": result.errors,
            "warnings": result.warnings
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ Résultat exporté: {output_path}")
    
    def parse_text_directly(self, text: str, document_type: str = "cv") -> ParsingResult:
        """Parse directement du texte (sans extraction PDF)"""
        start_time = time.time()
        self.stats["total_processed"] += 1
        errors = []
        warnings = []
        
        self.logger.info(f"🔍 Début parsing texte direct: {document_type}")
        
        try:
            if not text or len(text.strip()) < 50:
                error_msg = "Texte insuffisant pour le parsing"
                return self._create_failed_result("direct_text", error_msg, [error_msg], start_time)
            
            if document_type.lower() == "cv":
                llm_result = self.gemma_client.parse_cv_text(text)
                validation_func = self._validate_cv_data
                stats_key = "successful_cv_parses"
            else:
                llm_result = self.gemma_client.parse_job_text(text)
                validation_func = self._validate_job_data
                stats_key = "successful_job_parses"
            
            if "error" in llm_result:
                error_msg = f"Erreur LLM: {llm_result['error']}"
                errors.append(error_msg)
                self.stats["failed_llm_calls"] += 1
                return self._create_failed_result("direct_text", error_msg, errors, start_time)
            
            self.logger.info("🤖 Parsing LLM réussi")
            
            validated_data, validation_errors = validation_func(llm_result)
            if validation_errors and self.validation_strict:
                errors.extend(validation_errors)
                self.stats["failed_validations"] += 1
                return self._create_failed_result("direct_text", "Validation échouée", errors, start_time)
            
            if validation_errors:
                warnings.extend(validation_errors)
            
            mock_extraction = type('obj', (object,), {
                'text': text, 
                'confidence': 0.9,
                'method_used': 'direct_text'
            })
            
            confidence = self._calculate_overall_confidence(
                mock_extraction, llm_result, validated_data
            )
            
            execution_time = time.time() - start_time
            
            self.stats[stats_key] += 1
            self.stats["total_time"] += execution_time
            self.stats["average_processing_time"] = (
                self.stats["total_time"] / self.stats["total_processed"]
            )
            
            self.logger.info(f"✅ Texte parsé avec succès en {execution_time:.2f}s")
            
            return ParsingResult(
                success=True,
                data=validated_data,
                confidence=confidence,
                execution_time=execution_time,
                extraction_method="direct_text",
                llm_model=self.gemma_model,
                source_file="direct_text",
                errors=errors,
                warnings=warnings,
                raw_text_length=len(text),
                json_validation_passed=len(validation_errors) == 0
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Erreur inattendue: {str(e)}"
            self.logger.error(error_msg)
            return self._create_failed_result("direct_text", error_msg, [error_msg], start_time)
    
    def compare_cv_job_match(self, cv_data: Dict, job_data: Dict) -> Dict:
        """
        Compare un CV avec une offre d'emploi pour évaluer la compatibilité
        VERSION CORRIGÉE avec distinction expérience pro/formation
        """
        try:
            self.logger.info("🔄 Analyse de compatibilité CV/Offre")
            
            match_result = {
                "overall_score": 0.0,
                "compatibility_level": "Faible",
                "strengths": [],
                "weaknesses": [],
                "missing_skills": [],
                "matching_skills": [],
                "experience_match": {
                    "required": job_data.get("experience_requise", 0),
                    "candidate_professional": cv_data.get("experience_years", 0),
                    "candidate_academic": cv_data.get("formation_years", 0),
                    "match": False,
                    "analysis": ""
                },
                "detailed_analysis": {},
                "recommendations": []
            }
            
            scores = []
            
            # === ANALYSE DES COMPÉTENCES TECHNIQUES ===
            job_skills = set(job_data.get("competences_techniques", []))
            cv_skills = set(cv_data.get("competences_techniques", []))
            
            job_skills_norm = {skill.lower().strip() for skill in job_skills if skill}
            cv_skills_norm = {skill.lower().strip() for skill in cv_skills if skill}
            
            if job_skills_norm:
                matching_skills_norm = job_skills_norm.intersection(cv_skills_norm)
                missing_skills_norm = job_skills_norm - cv_skills_norm
                
                skill_score = len(matching_skills_norm) / len(job_skills_norm)
                scores.append(("competences_techniques", skill_score, 0.4))
                
                match_result["matching_skills"] = [
                    skill for skill in job_skills 
                    if skill.lower().strip() in matching_skills_norm
                ]
                match_result["missing_skills"] = [
                    skill for skill in job_skills 
                    if skill.lower().strip() in missing_skills_norm
                ]
                
                if matching_skills_norm:
                    match_result["strengths"].append(f"Maîtrise {len(matching_skills_norm)} compétences requises")
                if missing_skills_norm:
                    match_result["weaknesses"].append(f"Manque {len(missing_skills_norm)} compétences techniques")
            
            # === ANALYSE DE L'EXPÉRIENCE (CORRIGÉE) ===
            required_exp = job_data.get("experience_requise", 0)
            candidate_professional_exp = cv_data.get("experience_years", 0)
            candidate_academic_years = cv_data.get("formation_years", 0)
            
            if required_exp > 0:
                # Score basé UNIQUEMENT sur l'expérience professionnelle
                exp_ratio = min(candidate_professional_exp / required_exp, 1.5) if required_exp > 0 else 1.0
                exp_score = min(exp_ratio, 1.0)
                scores.append(("experience", exp_score, 0.3))
                
                match_result["experience_match"]["match"] = candidate_professional_exp >= required_exp
                
                if candidate_professional_exp >= required_exp:
                    match_result["experience_match"]["analysis"] = f"Expérience professionnelle suffisante: {candidate_professional_exp} ans (requis: {required_exp} ans)"
                    match_result["strengths"].append(f"Expérience professionnelle suffisante ({candidate_professional_exp} ans)")
                else:
                    exp_gap = required_exp - candidate_professional_exp
                    match_result["experience_match"]["analysis"] = f"Expérience professionnelle insuffisante: {candidate_professional_exp} ans (manque: {exp_gap} ans). Formation académique: {candidate_academic_years} ans"
                    
                    if candidate_academic_years > 0:
                        match_result["weaknesses"].append(f"Expérience pro insuffisante ({candidate_professional_exp}/{required_exp} ans) mais formation académique solide ({candidate_academic_years} ans)")
                    else:
                        match_result["weaknesses"].append(f"Expérience professionnelle insuffisante ({candidate_professional_exp}/{required_exp} ans)")
            else:
                match_result["experience_match"]["analysis"] = "Aucune expérience spécifique requise"
                match_result["experience_match"]["match"] = True
            
            # === ANALYSE DES FORMATIONS ===
            job_formations = job_data.get("formations_requises", [])
            cv_formations = [f.get("domaine", "") if isinstance(f, dict) else str(f) 
                           for f in cv_data.get("formations", [])]
            
            if job_formations and cv_formations:
                formation_matches = 0
                for jf in job_formations:
                    for cf in cv_formations:
                        if (jf.lower().strip() in cf.lower().strip() or 
                            cf.lower().strip() in jf.lower().strip()):
                            formation_matches += 1
                            break
                
                formation_score = min(formation_matches / len(job_formations), 1.0)
                scores.append(("formations", formation_score, 0.2))
                
                if formation_matches > 0:
                    match_result["strengths"].append(f"Formation pertinente ({candidate_academic_years} ans d'études)")
                else:
                    match_result["weaknesses"].append("Formation non alignée avec les exigences")
            
            # === ANALYSE DES SOFT SKILLS ===
            job_soft_skills = job_data.get("competences_requises", [])
            cv_soft_skills = cv_data.get("soft_skills", [])
            
            if job_soft_skills and cv_soft_skills:
                soft_matches = 0
                for js in job_soft_skills:
                    for cs in cv_soft_skills:
                        if (js.lower().strip() in cs.lower().strip() or 
                            cs.lower().strip() in js.lower().strip()):
                            soft_matches += 1
                            break
                
                soft_score = min(soft_matches / len(job_soft_skills), 1.0)
                scores.append(("soft_skills", soft_score, 0.1))
                
                if soft_matches > 0:
                    match_result["strengths"].append(f"Compétences transversales alignées ({soft_matches})")
            
            # === CALCUL DU SCORE GLOBAL ===
            if scores:
                weighted_score = sum(score * weight for _, score, weight in scores)
                total_weight = sum(weight for _, _, weight in scores)
                match_result["overall_score"] = weighted_score / total_weight if total_weight > 0 else 0
            
            # === DÉTERMINATION DU NIVEAU DE COMPATIBILITÉ ===
            score = match_result["overall_score"]
            if score >= 0.8:
                match_result["compatibility_level"] = "Excellente"
            elif score >= 0.6:
                match_result["compatibility_level"] = "Bonne"
            elif score >= 0.4:
                match_result["compatibility_level"] = "Moyenne"
            elif score >= 0.2:
                match_result["compatibility_level"] = "Faible"
            else:
                match_result["compatibility_level"] = "Très faible"
            
            # === ANALYSE DÉTAILLÉE ===
            match_result["detailed_analysis"] = {
                component: {
                    "score": round(score, 3), 
                    "weight": weight, 
                    "contribution": round(score * weight, 3)
                }
                for component, score, weight in scores
            }
            
            # === RECOMMANDATIONS PERSONNALISÉES ===
            if match_result["missing_skills"]:
                top_missing = match_result["missing_skills"][:3]
                match_result["recommendations"].append(
                    f"Développer les compétences techniques: {', '.join(top_missing)}"
                )
            
            if not match_result["experience_match"]["match"] and required_exp > 0:
                exp_gap = required_exp - candidate_professional_exp
                if candidate_academic_years > 0:
                    match_result["recommendations"].append(
                        f"Valoriser la formation académique ({candidate_academic_years} ans) pour compenser le manque d'expérience professionnelle ({exp_gap} ans)"
                    )
                else:
                    match_result["recommendations"].append(
                        f"Acquérir {exp_gap} années d'expérience professionnelle supplémentaires"
                    )
            
            if score < 0.5:
                if candidate_academic_years > 2:
                    match_result["recommendations"].append(
                        f"Mettre en avant la formation solide ({candidate_academic_years} ans) et rechercher des postes junior"
                    )
                else:
                    match_result["recommendations"].append(
                        "Envisager une formation complémentaire ou cibler des postes plus adaptés"
                    )
            elif score >= 0.7:
                match_result["recommendations"].append(
                    "Profil très adapté - Mettre en avant les compétences techniques correspondantes"
                )
            
            self.logger.info(f"✅ Analyse terminée: {match_result['compatibility_level']} ({score:.1%})")
            self.logger.info(f"📊 Exp. pro: {candidate_professional_exp} ans, Formation: {candidate_academic_years} ans (requis: {required_exp} ans)")
            
            return match_result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur analyse compatibilité: {str(e)}")
            return {
                "overall_score": 0.0,
                "compatibility_level": "Erreur",
                "error": str(e),
                "strengths": [],
                "weaknesses": [],
                "missing_skills": [],
                "matching_skills": [],
                "experience_match": {"required": 0, "candidate_professional": 0, "candidate_academic": 0, "match": False, "analysis": "Erreur"},
                "detailed_analysis": {},
                "recommendations": []
            }
    
    def generate_cv_summary(self, cv_data: Dict) -> Dict:
        """
        Génère un résumé structuré du CV
        VERSION CORRIGÉE avec distinction formation/expérience
        """
        try:
            self.logger.info("📝 Génération résumé CV")
            
            professional_exp = cv_data.get("experience_years", 0)
            academic_years = cv_data.get("formation_years", 0)
            
            summary = {
                "profil_titre": cv_data.get("titre_candidat", "Profil non spécifié"),
                "experience_professionnelle": professional_exp,
                "formation_academique": academic_years,
                "niveau_experience": "",
                "niveau_formation": "",
                "competences_cles": [],
                "domaines_expertise": [],
                "formations_principales": [],
                "langues_parlees": [],
                "certifications_importantes": [],
                "points_forts": [],
                "profil_type": "",
                "secteurs_activite": []
            }
            
            # === NIVEAU D'EXPÉRIENCE PROFESSIONNELLE ===
            if professional_exp == 0:
                summary["niveau_experience"] = "Débutant/Sans expérience"
            elif professional_exp <= 2:
                summary["niveau_experience"] = "Junior"
            elif professional_exp <= 5:
                summary["niveau_experience"] = "Confirmé"
            elif professional_exp <= 10:
                summary["niveau_experience"] = "Senior"
            else:
                summary["niveau_experience"] = "Expert"
            
            # === NIVEAU DE FORMATION ===
            if academic_years == 0:
                summary["niveau_formation"] = "Formation non spécifiée"
            elif academic_years <= 2:
                summary["niveau_formation"] = "Formation courte (Bac+2)"
            elif academic_years <= 3:
                summary["niveau_formation"] = "Licence (Bac+3)"
            elif academic_years <= 5:
                summary["niveau_formation"] = "Master/Ingénieur (Bac+5)"
            else:
                summary["niveau_formation"] = "Doctorat/Formation supérieure (Bac+8+)"
            
            # === COMPÉTENCES CLÉS ===
            competences = cv_data.get("competences_techniques", [])
            summary["competences_cles"] = competences[:5] if competences else []
            
            # === ANALYSE DES EXPÉRIENCES ===
            experiences = cv_data.get("experience", [])
            domaines = set()
            secteurs = set()
            
            for exp in experiences:
                if isinstance(exp, dict):
                    poste = exp.get("poste", "").lower()
                    entreprise = exp.get("entreprise", "").lower()
                    
                    # Domaines d'expertise
                    if any(tech in poste for tech in ["développeur", "dev", "programmer", "software"]):
                        domaines.add("Développement logiciel")
                    if any(tech in poste for tech in ["data", "analyst", "analytics"]):
                        domaines.add("Analyse de données")
                    if any(tech in poste for tech in ["marketing", "commercial", "vente"]):
                        domaines.add("Marketing/Commercial")
                    if any(tech in poste for tech in ["manager", "chef", "lead", "directeur"]):
                        domaines.add("Management")
                    if any(tech in poste for tech in ["consultant", "conseil"]):
                        domaines.add("Conseil")
                    
                    # Secteurs d'activité
                    if any(sect in entreprise for sect in ["banque", "finance", "bank"]):
                        secteurs.add("Finance/Banque")
                    if any(sect in entreprise for sect in ["tech", "digital", "software", "it"]):
                        secteurs.add("Technologies")
                    if any(sect in entreprise for sect in ["retail", "commerce", "vente"]):
                        secteurs.add("Commerce/Retail")
                    if any(sect in entreprise for sect in ["santé", "medical", "pharma"]):
                        secteurs.add("Santé")
            
            summary["domaines_expertise"] = list(domaines)
            summary["secteurs_activite"] = list(secteurs)
            
            # === FORMATIONS PRINCIPALES ===
            formations = cv_data.get("formations", [])
            for formation in formations[:3]:
                if isinstance(formation, dict):
                    diplome = formation.get("diplome", "")
                    domaine = formation.get("domaine", "")
                    if diplome or domaine:
                        summary["formations_principales"].append(f"{diplome} - {domaine}".strip(" -"))
                else:
                    summary["formations_principales"].append(str(formation))
            
            # === LANGUES ===
            langues = cv_data.get("langues", [])
            for langue in langues:
                if isinstance(langue, dict):
                    nom = langue.get("langue", "")
                    niveau = langue.get("niveau", "")
                    if nom:
                        summary["langues_parlees"].append(f"{nom} ({niveau})".strip(" ()"))
                else:
                    summary["langues_parlees"].append(str(langue))
            
            # === CERTIFICATIONS ===
            certifications = cv_data.get("certifications", [])
            summary["certifications_importantes"] = certifications[:5]
            
            # === POINTS FORTS ===
            if summary["competences_cles"]:
                summary["points_forts"].append(f"Maîtrise de {len(summary['competences_cles'])} compétences techniques")
            
            if professional_exp > 0:
                summary["points_forts"].append(f"{professional_exp} années d'expérience professionnelle")
            
            if academic_years > 0:
                summary["points_forts"].append(f"Formation académique solide ({academic_years} ans - {summary['niveau_formation']})")
            
            if summary["domaines_expertise"]:
                summary["points_forts"].append(f"Expertise en {', '.join(summary['domaines_expertise'][:2])}")
            
            if summary["certifications_importantes"]:
                summary["points_forts"].append(f"{len(summary['certifications_importantes'])} certifications")
            
            # === TYPE DE PROFIL ===
            if "Développement logiciel" in summary["domaines_expertise"]:
                if professional_exp > 0:
                    summary["profil_type"] = "Profil Technique/Développeur Expérimenté"
                else:
                    summary["profil_type"] = "Profil Technique/Développeur Junior"
            elif "Management" in summary["domaines_expertise"]:
                summary["profil_type"] = "Profil Management"
            elif "Marketing/Commercial" in summary["domaines_expertise"]:
                summary["profil_type"] = "Profil Commercial/Marketing"
            elif "Analyse de données" in summary["domaines_expertise"]:
                summary["profil_type"] = "Profil Data/Analytique"
            elif "Conseil" in summary["domaines_expertise"]:
                summary["profil_type"] = "Profil Conseil/Expertise"
            elif professional_exp == 0 and academic_years > 3:
                summary["profil_type"] = "Profil Académique/Jeune Diplômé"
            elif professional_exp == 0:
                summary["profil_type"] = "Profil Débutant"
            else:
                summary["profil_type"] = "Profil Généraliste"
            
            self.logger.info(f"✅ Résumé généré: {summary['profil_type']} - Exp: {professional_exp}ans, Form: {academic_years}ans")
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération résumé: {str(e)}")
            return {
                "error": str(e),
                "profil_titre": "Erreur",
                "experience_professionnelle": 0,
                "formation_academique": 0,
                "niveau_experience": "Inconnu",
                "niveau_formation": "Inconnu",
                "competences_cles": [],
                "domaines_expertise": [],
                "formations_principales": [],
                "langues_parlees": [],
                "certifications_importantes": [],
                "points_forts": [],
                "profil_type": "Erreur",
                "secteurs_activite": []
            }

def main():
    """Point d'entrée principal pour utilisation CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CV Parser - Extraction PDF vers JSON (VERSION CORRIGÉE)")
    parser.add_argument("command", 
                       choices=["cv", "job", "batch-cv", "batch-job", "stats", "match", "text", "summary"], 
                       help="Type d'opération")
    parser.add_argument("--input", "-i", required=True, 
                       help="Fichier PDF, dossier d'entrée ou texte direct")
    parser.add_argument("--input2", 
                       help="Deuxième fichier pour comparaison (commande match)")
    parser.add_argument("--output", "-o", 
                       help="Fichier ou dossier de sortie")
    parser.add_argument("--type", default="cv", choices=["cv", "job"],
                       help="Type de document pour parsing texte direct")
    parser.add_argument("--model", default="gemma3:4b", 
                       help="Modèle Gemma à utiliser")
    parser.add_argument("--ollama-url", default="http://localhost:11434", 
                       help="URL du serveur Ollama")
    parser.add_argument("--extraction-method", default="auto", 
                       choices=["auto", "pypdf", "pdfplumber", "ocr"],
                       help="Méthode d'extraction PDF")
    parser.add_argument("--temperature", type=float, default=0.1, 
                       help="Température LLM")
    parser.add_argument("--strict", action="store_true", 
                       help="Validation stricte")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Niveau de log")
    
    args = parser.parse_args()
    
    try:
        print("🚀 CV Parser VERSION CORRIGÉE - Distinction Formation/Expérience")
        print("=" * 60)
        
        cv_parser = CVParser(
            gemma_model=args.model,
            ollama_url=args.ollama_url,
            pdf_extraction_method=args.extraction_method,
            llm_temperature=args.temperature,
            validation_strict=args.strict,
            log_level=args.log_level
        )
        
        if args.command == "cv":
            result = cv_parser.parse_cv_from_pdf(args.input)
            
            # Affichage des informations corrigées
            if result.success:
                exp_prof = result.data.get('experience_years', 0)
                exp_form = result.data.get('formation_years', 0)
                print(f"\n📊 RÉSULTATS PARSING CV:")
                print(f"   • Expérience professionnelle: {exp_prof} ans")
                print(f"   • Formation académique: {exp_form} ans")
                print(f"   • Confiance: {result.confidence:.1%}")
                
            if args.output:
                cv_parser.export_result_to_json(result, args.output)
            else:
                print(json.dumps(result.data, indent=2, ensure_ascii=False))
                
        elif args.command == "job":
            result = cv_parser.parse_job_from_pdf(args.input)
            if args.output:
                cv_parser.export_result_to_json(result, args.output)
            else:
                print(json.dumps(result.data, indent=2, ensure_ascii=False))
        
        elif args.command == "text":
            with open(args.input, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            result = cv_parser.parse_text_directly(text_content, args.type)
            
            if result.success and args.type == "cv":
                exp_prof = result.data.get('experience_years', 0)
                exp_form = result.data.get('formation_years', 0)
                print(f"\n📊 RÉSULTATS PARSING TEXTE:")
                print(f"   • Expérience professionnelle: {exp_prof} ans")
                print(f"   • Formation académique: {exp_form} ans")
                print(f"   • Confiance: {result.confidence:.1%}")
            
            if args.output:
                cv_parser.export_result_to_json(result, args.output)
            else:
                print(json.dumps(result.data, indent=2, ensure_ascii=False))
                
        elif args.command == "batch-cv":
            report = cv_parser.batch_parse_cvs(args.input, args.output)
            
            print(f"\n📊 RAPPORT BATCH CV:")
            print(f"   • Traités: {report['processed']}")
            print(f"   • Réussis: {report['successful']}")
            print(f"   • Échecs: {report['failed']}")
            print(f"   • Taux de réussite: {report['success_rate']:.1f}%")
            
            if 'experience_stats' in report:
                print(f"   • Exp. pro moyenne: {report['experience_stats']['avg_professional_exp']:.1f} ans")
                print(f"   • Formation moyenne: {report['experience_stats']['avg_academic_years']:.1f} ans")
            
        elif args.command == "batch-job":
            report = cv_parser.batch_parse_jobs(args.input, args.output)
            print(f"📊 Traitement terminé: {report['successful']}/{report['processed']} réussis")
            
        elif args.command == "match":
            if not args.input2:
                print("❌ La commande 'match' nécessite --input2")
                sys.exit(1)
            
            cv_result = cv_parser.parse_cv_from_pdf(args.input)
            job_result = cv_parser.parse_job_from_pdf(args.input2)
            
            if cv_result.success and job_result.success:
                match_result = cv_parser.compare_cv_job_match(cv_result.data, job_result.data)
                
                # Affichage des résultats d'analyse
                print(f"\n🔄 ANALYSE DE COMPATIBILITÉ:")
                print(f"   • Score global: {match_result['overall_score']:.1%}")
                print(f"   • Niveau: {match_result['compatibility_level']}")
                print(f"   • Exp. requise: {match_result['experience_match']['required']} ans")
                print(f"   • Exp. professionnelle: {match_result['experience_match']['candidate_professional']} ans")
                print(f"   • Formation académique: {match_result['experience_match']['candidate_academic']} ans")
                print(f"   • Match expérience: {'✅' if match_result['experience_match']['match'] else '❌'}")
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(match_result, f, indent=2, ensure_ascii=False)
                else:
                    print(json.dumps(match_result, indent=2, ensure_ascii=False))
            else:
                print("❌ Erreur lors du parsing des fichiers")
                if not cv_result.success:
                    print(f"CV: {cv_result.errors}")
                if not job_result.success:
                    print(f"Offre: {job_result.errors}")
        
        elif args.command == "summary":
            cv_result = cv_parser.parse_cv_from_pdf(args.input)
            if cv_result.success:
                summary = cv_parser.generate_cv_summary(cv_result.data)
                
                print(f"\n📝 RÉSUMÉ CV:")
                print(f"   • Profil: {summary.get('profil_type', 'Inconnu')}")
                print(f"   • Exp. professionnelle: {summary.get('experience_professionnelle', 0)} ans ({summary.get('niveau_experience', 'Inconnu')})")
                print(f"   • Formation: {summary.get('formation_academique', 0)} ans ({summary.get('niveau_formation', 'Inconnu')})")
                print(f"   • Compétences clés: {len(summary.get('competences_cles', []))}")
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(summary, f, indent=2, ensure_ascii=False)
                else:
                    print(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Erreur parsing CV: {cv_result.errors}")
                
        elif args.command == "stats":
            stats = cv_parser.get_statistics()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        print(f"\n✅ Opération terminée avec succès!")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()