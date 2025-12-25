# cv_parser_with_db.py - VERSION OPTIMISÉE SANS REDONDANCES
# Script principal qui combine CV parser et sauvegarde en base de données
# À placer dans le dossier ai_engine/services/

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Optional

# Import des services locaux
try:
    from cv_parser import CVParser
    from cv_database_manager import CVDatabaseManager
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Vérifiez que cv_parser.py et cv_database_manager.py sont dans le même dossier")
    sys.exit(1)


class CVParserWithDatabase:
    """
    Service principal qui combine parsing CV et sauvegarde base de données
    VERSION OPTIMISÉE - Élimine toutes les redondances
    """

    def __init__(self,
                 gemma_model: str = "gemma3:4b",
                 ollama_url: str = "http://localhost:11434",
                 pdf_extraction_method: str = "auto",
                 llm_temperature: float = 0.1,
                 validation_strict: bool = True,
                 log_level: str = "INFO"):

        self.setup_logging(log_level)

        # Initialiser les services
        try:
            self.cv_parser = CVParser(
                gemma_model=gemma_model,
                ollama_url=ollama_url,
                pdf_extraction_method=pdf_extraction_method,
                llm_temperature=llm_temperature,
                validation_strict=validation_strict,
                log_level=log_level
            )
            self.logger.info("✅ CVParser initialisé")

            self.db_manager = CVDatabaseManager(log_level=log_level)
            self.logger.info("✅ CVDatabaseManager initialisé")

        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation services: {str(e)}")
            raise Exception(f"Impossible d'initialiser les services: {str(e)}")

        # Statistiques simplifiées - PAS DE DUPLICATION
        self.processing_stats = {
            "files_processed": 0,
            "parsing_successes": 0,
            "database_saves": 0,
            "quality_issues": 0
        }

    def setup_logging(self, log_level: str):
        """Configuration du logging centralisé"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'cv_parser_with_db.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CVParserWithDB')

    def health_check(self) -> Dict:
        """Vérification de l'état de tous les services - RÉUTILISE les services existants"""
        health_status = {
            "cv_parser": {"status": "unknown", "details": ""},
            "database": {"status": "unknown", "details": ""},
            "overall_status": "unknown"
        }

        try:
            # RÉUTILISER les stats du CVParser existant
            parser_stats = self.cv_parser.get_statistics()
            if parser_stats["services_status"]["gemma_client"]["status"] == "healthy":
                health_status["cv_parser"]["status"] = "healthy"
                health_status["cv_parser"]["details"] = "CV Parser opérationnel"
            else:
                health_status["cv_parser"]["status"] = "unhealthy"
                health_status["cv_parser"]["details"] = "CV Parser non opérationnel"
        except Exception as e:
            health_status["cv_parser"]["status"] = "error"
            health_status["cv_parser"]["details"] = f"Erreur CV Parser: {str(e)}"

        try:
            # RÉUTILISER le test database du CVDatabaseManager
            db_test = self.db_manager.test_database_connection()
            health_status["database"]["status"] = "healthy" if db_test["status"] == "success" else "unhealthy"
            health_status["database"]["details"] = db_test["message"]
        except Exception as e:
            health_status["database"]["status"] = "error"
            health_status["database"]["details"] = f"Erreur Database: {str(e)}"

        # Statut global
        if (health_status["cv_parser"]["status"] == "healthy" and
                health_status["database"]["status"] == "healthy"):
            health_status["overall_status"] = "healthy"
        else:
            health_status["overall_status"] = "unhealthy"

        return health_status

    def process_single_cv(self, pdf_path: str, save_to_db: bool = True) -> Dict:
        """
        VERSION OPTIMISÉE - Traite un seul CV sans duplication
        UTILISE UNIQUEMENT les extracteurs robustes du CVDatabaseManager
        """
        self.logger.info(f"📄 Traitement CV: {pdf_path}")
        self.processing_stats["files_processed"] += 1

        # ÉTAPE 1: Parsing du CV (CVParser)
        parsing_result = self.cv_parser.parse_cv_from_pdf(pdf_path)

        # Structure de retour unifiée
        result = {
            "source_file": pdf_path,
            "parsing_success": parsing_result.success,
            "parsing_confidence": parsing_result.confidence,
            "parsing_time": parsing_result.execution_time,
            "database_save_success": False,
            "candidate_id": None,
            "cv_data": parsing_result.data if parsing_result.success else {},
            "errors": parsing_result.errors.copy(),
            "warnings": parsing_result.warnings.copy(),
            "message": "",
            "extracted_candidate_info": {},  # UTILISE l'extracteur robuste du DB Manager
            "data_quality_score": 0.0
        }

        if not parsing_result.success:
            result["message"] = f"Échec parsing CV: {', '.join(parsing_result.errors)}"
            self.logger.error(f"❌ {result['message']}")
            return result

        self.processing_stats["parsing_successes"] += 1

        # ÉTAPE 2: Extraction des données candidat (CVDatabaseManager - PLUS ROBUSTE)
        if parsing_result.data:
            # UTILISE l'extracteur robuste du CVDatabaseManager
            extracted_candidate_data = self.db_manager.extractor.extract(parsing_result.data)

            # Convertir CandidateData en dict pour compatibilité
            result["extracted_candidate_info"] = {
                "first_name": extracted_candidate_data.first_name,
                "last_name": extracted_candidate_data.last_name,
                "professional_title": extracted_candidate_data.professional_title,
                "email": extracted_candidate_data.email,
                "phone": extracted_candidate_data.phone,
                "address": extracted_candidate_data.address,
                "city": extracted_candidate_data.city,
                "linkedin_url": extracted_candidate_data.linkedin_url,
                "gender": extracted_candidate_data.gender,
                "birth_date": extracted_candidate_data.birth_date,
                "experience_years": extracted_candidate_data.experience_years,
                "education_level": extracted_candidate_data.education_level,
                "skills_count": len(extracted_candidate_data.skills_extracted),
                "skills_extracted": extracted_candidate_data.skills_extracted,
                "languages": extracted_candidate_data.languages,
                "ai_summary": extracted_candidate_data.ai_summary,
                "cv_embeddings": extracted_candidate_data.cv_embeddings
            }

            # UTILISE le calcul de qualité robuste du CVDatabaseManager
            result["data_quality_score"] = self._calculate_unified_quality_score(
                result["extracted_candidate_info"],
                parsing_result.confidence
            )

        # Affichage des informations extraites
        if result["extracted_candidate_info"]:
            candidate_info = result["extracted_candidate_info"]
            self.logger.info(f"📊 CV parsé: {candidate_info.get('professional_title', 'Inconnu')}")
            self.logger.info(f"   • Nom: {candidate_info.get('first_name')} {candidate_info.get('last_name')}")
            self.logger.info(f"   • Expérience: {candidate_info.get('experience_years', 0)} ans")
            self.logger.info(f"   • Compétences: {candidate_info.get('skills_count', 0)}")
            self.logger.info(f"   • Qualité des données: {result['data_quality_score']:.1%}")
            self.logger.info(f"   • Confiance parsing: {parsing_result.confidence:.1%}")

            # Vérifier la qualité des données
            if result["data_quality_score"] < 0.5:
                self.processing_stats["quality_issues"] += 1
                result["warnings"].append(f"Qualité des données faible ({result['data_quality_score']:.1%})")

        # ÉTAPE 3: Sauvegarde en base de données (si demandée)
        if save_to_db and parsing_result.success:
            self.logger.info("💾 Sauvegarde en base de données...")

            # Obtenir le texte brut du CV
            raw_cv_text = getattr(parsing_result, 'raw_text_content', '')
            if not raw_cv_text:
                try:
                    extraction_result = self.cv_parser._extract_text_from_pdf(pdf_path)
                    raw_cv_text = getattr(extraction_result, 'text', '')[:10000]
                except Exception as e:
                    self.logger.warning(f"⚠️ Impossible de récupérer le texte brut: {str(e)}")

            # UTILISE la méthode robuste du CVDatabaseManager
            success, message, candidate_id = self.db_manager.save_candidate(
                parsing_result.data,
                pdf_path,
                raw_cv_text
            )

            result["database_save_success"] = success
            result["candidate_id"] = candidate_id

            if success:
                self.processing_stats["database_saves"] += 1
                result["message"] = f"CV traité et sauvegardé avec succès (Candidat ID: {candidate_id})"
                self.logger.info(f"✅ {result['message']}")
            else:
                result["message"] = f"CV parsé mais échec sauvegarde: {message}"
                result["errors"].append(message)
                self.logger.error(f"❌ {result['message']}")
        else:
            result[
                "message"] = "CV parsé avec succès (pas de sauvegarde demandée)" if not save_to_db else "CV parsé avec succès"
            self.logger.info(f"✅ {result['message']}")

        return result

    def _calculate_unified_quality_score(self, extracted_info: Dict, parsing_confidence: float) -> float:
        """
        Calcule un score de qualité unifié en combinant:
        - La qualité des données extraites
        - La confiance du parsing LLM
        MÉTHODE UNIQUE - pas de duplication
        """
        data_score = 0.0
        total_weight = 0.0

        # Pondération des champs par importance
        field_weights = {
            'first_name': 0.15,
            'last_name': 0.15,
            'email': 0.20,
            'phone': 0.10,
            'professional_title': 0.15,
            'experience_years': 0.10,
            'skills_count': 0.10,
            'education_level': 0.05
        }

        for field, weight in field_weights.items():
            total_weight += weight
            value = extracted_info.get(field, '')

            if field == 'skills_count':
                if value > 0:
                    data_score += weight * min(value / 5.0, 1.0)
            elif field == 'experience_years':
                if value > 0:
                    data_score += weight
            else:
                if value and str(value).strip() and str(value).lower() not in ['nan', 'none', '']:
                    data_score += weight

        data_quality = data_score / total_weight if total_weight > 0 else 0.0

        # Score combiné: 70% qualité données + 30% confiance parsing
        return (data_quality * 0.7) + (parsing_confidence * 0.3)

    def process_batch_cvs(self, pdf_directory: str, save_to_db: bool = True, output_directory: str = None) -> Dict:
        """
        VERSION OPTIMISÉE - Traite un lot de CVs sans duplication de code
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Dossier non trouvé: {pdf_directory}")

        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            self.logger.warning(f"Aucun fichier PDF trouvé dans {pdf_directory}")
            return {"processed": 0, "successful": 0, "failed": 0, "results": []}

        self.logger.info(f"🚀 Début traitement par lot: {len(pdf_files)} CVs")
        self.logger.info(f"💾 Sauvegarde en DB: {'Oui' if save_to_db else 'Non'}")

        if output_directory:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Sortie JSON: {output_directory}")

        batch_results = []
        successful = 0
        failed = 0

        for pdf_file in pdf_files:
            try:
                # RÉUTILISE process_single_cv - PAS DE DUPLICATION
                cv_result = self.process_single_cv(str(pdf_file), save_to_db)

                candidate_info = cv_result["extracted_candidate_info"]

                batch_results.append({
                    "file": pdf_file.name,
                    "parsing_success": cv_result["parsing_success"],
                    "database_save_success": cv_result["database_save_success"],
                    "candidate_id": cv_result["candidate_id"],
                    "confidence": cv_result["parsing_confidence"],
                    "execution_time": cv_result["parsing_time"],
                    "data_quality_score": cv_result["data_quality_score"],
                    "first_name": candidate_info.get("first_name", ""),
                    "last_name": candidate_info.get("last_name", ""),
                    "professional_title": candidate_info.get("professional_title", ""),
                    "email": candidate_info.get("email", ""),
                    "phone": candidate_info.get("phone", ""),
                    "experience_years": candidate_info.get("experience_years", 0),
                    "skills_count": candidate_info.get("skills_count", 0),
                    "education_level": candidate_info.get("education_level", ""),
                    "message": cv_result["message"],
                    "errors": cv_result["errors"],
                    "warnings": cv_result["warnings"]
                })

                # Compter les succès selon le critère
                success_criteria = cv_result["database_save_success"] if save_to_db else cv_result["parsing_success"]
                if success_criteria:
                    successful += 1
                else:
                    failed += 1

                # Sauvegarde JSON individuelle si demandée
                if output_directory and cv_result["parsing_success"]:
                    output_file = output_dir / f"{pdf_file.stem}_parsed.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "metadata": {
                                "source_file": pdf_file.name,
                                "parsing_date": datetime.now().isoformat(),
                                "confidence": cv_result["parsing_confidence"],
                                "execution_time": cv_result["parsing_time"],
                                "database_saved": cv_result["database_save_success"],
                                "candidate_id": cv_result["candidate_id"],
                                "data_quality_score": cv_result["data_quality_score"]
                            },
                            "extracted_candidate_info": candidate_info,
                            "cv_data": cv_result["cv_data"]
                        }, f, indent=2, ensure_ascii=False)

            except Exception as e:
                failed += 1
                error_msg = f"Erreur inattendue pour {pdf_file.name}: {str(e)}"
                self.logger.error(error_msg)
                batch_results.append({
                    "file": pdf_file.name,
                    "parsing_success": False,
                    "database_save_success": False,
                    "candidate_id": None,
                    "confidence": 0.0,
                    "execution_time": 0.0,
                    "data_quality_score": 0.0,
                    "message": error_msg,
                    "errors": [error_msg],
                    "warnings": []
                })

        # Rapport final - RÉUTILISE les statistiques existantes
        batch_report = {
            "processed": len(pdf_files),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(pdf_files)) * 100 if pdf_files else 0,
            "total_time": sum(r["execution_time"] for r in batch_results),
            "average_time": sum(r["execution_time"] for r in batch_results) / len(
                batch_results) if batch_results else 0,
            "extraction_quality": self._calculate_batch_quality_metrics(batch_results),
            "cv_parser_stats": self.cv_parser.get_statistics()["global_stats"],
            "database_stats": self.db_manager.get_statistics(),
            "processing_stats": self.processing_stats.copy(),
            "results": batch_results
        }

        # Logging des résultats
        self.logger.info(f"📊 Traitement terminé: {successful}/{len(pdf_files)} réussis")
        if save_to_db:
            self.logger.info(f"💾 Candidats sauvegardés en DB: {self.processing_stats['database_saves']}")

        quality_stats = batch_report['extraction_quality']
        self.logger.info(f"📈 QUALITÉ D'EXTRACTION:")
        self.logger.info(f"   • Noms extraits: {quality_stats['candidates_with_names']}/{len(pdf_files)}")
        self.logger.info(f"   • Titres professionnels: {quality_stats['candidates_with_titles']}/{len(pdf_files)}")
        self.logger.info(f"   • Emails: {quality_stats['candidates_with_emails']}/{len(pdf_files)}")
        self.logger.info(f"   • Qualité moyenne: {quality_stats['average_data_quality']:.1%}")

        # Sauvegarde du rapport
        if output_directory:
            report_file = output_dir / "batch_report_optimized.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(batch_report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"📄 Rapport sauvegardé: {report_file}")

        return batch_report

    def _calculate_batch_quality_metrics(self, batch_results: list) -> Dict:
        """Calcule les métriques de qualité pour un lot - MÉTHODE UNIQUE"""
        return {
            "candidates_with_names": sum(1 for r in batch_results if r.get("first_name") and r.get("last_name")),
            "candidates_with_titles": sum(1 for r in batch_results if r.get("professional_title")),
            "candidates_with_emails": sum(1 for r in batch_results if r.get("email")),
            "candidates_with_phones": sum(1 for r in batch_results if r.get("phone")),
            "candidates_with_experience": sum(1 for r in batch_results if r.get("experience_years", 0) > 0),
            "average_data_quality": sum(r.get("data_quality_score", 0) for r in batch_results) / len(
                batch_results) if batch_results else 0,
            "high_quality_extractions": sum(1 for r in batch_results if r.get("data_quality_score", 0) >= 0.7)
        }

    def get_consolidated_statistics(self) -> Dict:
        """Retourne les statistiques consolidées - PAS DE DUPLICATION"""
        return {
            "cv_parser_stats": self.cv_parser.get_statistics(),
            "database_stats": self.db_manager.get_statistics(),
            "processing_stats": self.processing_stats.copy(),
            "health_check": self.health_check()
        }

    def test_complete_workflow(self, test_pdf_path: str) -> Dict:
        """Test complet du workflow - VERSION OPTIMISÉE"""
        self.logger.info("🧪 Test complet du workflow optimisé")

        test_result = {
            "test_file": test_pdf_path,
            "health_check": self.health_check(),
            "processing_result": None,
            "success": False,
            "message": ""
        }

        try:
            if test_result["health_check"]["overall_status"] != "healthy":
                test_result["message"] = "Services non opérationnels"
                return test_result

            # RÉUTILISE process_single_cv - PAS DE DUPLICATION
            processing_result = self.process_single_cv(test_pdf_path, save_to_db=True)
            test_result["processing_result"] = processing_result

            if processing_result["parsing_success"] and processing_result["database_save_success"]:
                test_result["success"] = True
                test_result["message"] = f"Test réussi - Candidat créé (ID: {processing_result['candidate_id']})"
            elif processing_result["parsing_success"]:
                test_result["message"] = "Parsing réussi mais échec sauvegarde DB"
            else:
                test_result["message"] = f"Échec parsing: {processing_result['message']}"

        except Exception as e:
            test_result["message"] = f"Erreur test: {str(e)}"

        return test_result


def main():
    """Interface en ligne de commande - VERSION OPTIMISÉE"""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="CV Parser avec Base de Données - VERSION OPTIMISÉE SANS REDONDANCES")
    parser.add_argument("command",
                        choices=["test-workflow", "process-cv", "batch-process", "health-check", "stats"],
                        help="Commande à exécuter")
    parser.add_argument("--input", "-i", help="Fichier PDF ou dossier d'entrée")
    parser.add_argument("--output", "-o", help="Dossier de sortie pour les JSONs")
    parser.add_argument("--no-db", action="store_true", help="Désactiver la sauvegarde en base de données")
    parser.add_argument("--model", default="gemma3:4b", help="Modèle Gemma à utiliser")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="URL du serveur Ollama")
    parser.add_argument("--extraction-method", default="auto",
                        choices=["auto", "pypdf", "pdfplumber", "ocr"],
                        help="Méthode d'extraction PDF")
    parser.add_argument("--temperature", type=float, default=0.1, help="Température LLM")
    parser.add_argument("--strict", action="store_true", help="Validation stricte")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Niveau de log")

    args = parser.parse_args()

    try:
        print("🚀 CV Parser avec Base de Données - VERSION OPTIMISÉE SANS REDONDANCES")
        print("=" * 70)

        # Initialisation du service principal
        cv_service = CVParserWithDatabase(
            gemma_model=args.model,
            ollama_url=args.ollama_url,
            pdf_extraction_method=args.extraction_method,
            llm_temperature=args.temperature,
            validation_strict=args.strict,
            log_level=args.log_level
        )

        if args.command == "health-check":
            health = cv_service.health_check()
            print(f"\n🏥 ÉTAT DES SERVICES:")
            print(f"   • CV Parser: {health['cv_parser']['status']} - {health['cv_parser']['details']}")
            print(f"   • Base de données: {health['database']['status']} - {health['database']['details']}")
            print(f"   • Statut global: {health['overall_status']}")

        elif args.command == "test-workflow":
            if not args.input:
                print("❌ --input (fichier PDF) requis pour test-workflow")
                sys.exit(1)

            test_result = cv_service.test_complete_workflow(args.input)
            print(f"\n🧪 TEST WORKFLOW COMPLET:")
            print(f"   • Fichier test: {Path(test_result['test_file']).name}")
            print(f"   • Succès: {'✅' if test_result['success'] else '❌'}")
            print(f"   • Message: {test_result['message']}")

            if test_result.get('processing_result'):
                pr = test_result['processing_result']
                if pr.get('extracted_candidate_info'):
                    extracted = pr['extracted_candidate_info']
                    print(f"\n📊 DONNÉES EXTRAITES:")
                    print(f"   • Nom: {extracted.get('first_name', '')} {extracted.get('last_name', '')}")
                    print(f"   • Titre: {extracted.get('professional_title', '')}")
                    print(f"   • Email: {extracted.get('email', '')}")
                    print(f"   • Téléphone: {extracted.get('phone', '')}")
                    print(f"   • Expérience: {extracted.get('experience_years', 0)} ans")
                    print(f"   • Compétences: {extracted.get('skills_count', 0)}")
                    print(f"   • Qualité données: {pr.get('data_quality_score', 0):.1%}")

        elif args.command == "process-cv":
            if not args.input:
                print("❌ --input (fichier PDF) requis pour process-cv")
                sys.exit(1)

            save_to_db = not args.no_db
            result = cv_service.process_single_cv(args.input, save_to_db)

            print(f"\n📄 TRAITEMENT CV:")
            print(f"   • Fichier: {Path(args.input).name}")
            print(f"   • Parsing: {'✅' if result['parsing_success'] else '❌'}")
            if save_to_db:
                print(f"   • Sauvegarde DB: {'✅' if result['database_save_success'] else '❌'}")
                if result['candidate_id']:
                    print(f"   • Candidat ID: {result['candidate_id']}")

            if result['parsing_success'] and result['extracted_candidate_info']:
                extracted = result['extracted_candidate_info']
                print(f"\n📊 INFORMATIONS EXTRAITES:")
                print(f"   • Nom: {extracted.get('first_name', '')} {extracted.get('last_name', '')}")
                print(f"   • Titre: {extracted.get('professional_title', '')}")
                print(f"   • Email: {extracted.get('email', '')}")
                print(f"   • Téléphone: {extracted.get('phone', '')}")
                print(f"   • Expérience: {extracted.get('experience_years', 0)} ans")
                print(f"   • Compétences: {extracted.get('skills_count', 0)}")
                print(f"   • Niveau éducation: {extracted.get('education_level', '')}")
                print(f"   • Qualité des données: {result['data_quality_score']:.1%}")
                print(f"   • Confiance: {result['parsing_confidence']:.1%}")

            print(f"   • Message: {result['message']}")

        elif args.command == "batch-process":
            if not args.input:
                print("❌ --input (dossier) requis pour batch-process")
                sys.exit(1)

            save_to_db = not args.no_db
            report = cv_service.process_batch_cvs(args.input, save_to_db, args.output)

            print(f"\n📊 RAPPORT BATCH OPTIMISÉ:")
            print(f"   • Fichiers traités: {report['processed']}")
            print(f"   • Succès: {report['successful']}")
            print(f"   • Échecs: {report['failed']}")
            print(f"   • Taux de réussite: {report['success_rate']:.1f}%")
            print(f"   • Temps total: {report['total_time']:.1f}s")
            print(f"   • Temps moyen: {report['average_time']:.1f}s/CV")

            if save_to_db:
                print(f"   • Candidats en DB: {report['processing_stats']['database_saves']}")

            quality_stats = report['extraction_quality']
            print(f"\n📈 QUALITÉ D'EXTRACTION:")
            print(f"   • Noms extraits: {quality_stats['candidates_with_names']}/{report['processed']}")
            print(f"   • Titres professionnels: {quality_stats['candidates_with_titles']}/{report['processed']}")
            print(f"   • Emails: {quality_stats['candidates_with_emails']}/{report['processed']}")
            print(f"   • Téléphones: {quality_stats['candidates_with_phones']}/{report['processed']}")
            print(f"   • Avec expérience: {quality_stats['candidates_with_experience']}/{report['processed']}")
            print(f"   • Qualité moyenne: {quality_stats['average_data_quality']:.1%}")
            print(f"   • Extractions haute qualité: {quality_stats['high_quality_extractions']}/{report['processed']}")

        elif args.command == "stats":
            stats = cv_service.get_consolidated_statistics()
            print(f"\n📊 STATISTIQUES CONSOLIDÉES:")

            cv_stats = stats['cv_parser_stats']['global_stats']
            print(f"   CV Parser:")
            print(f"     • Total traité: {cv_stats['total_processed']}")
            print(f"     • Parsing réussi: {cv_stats['successful_cv_parses']}")
            print(f"     • Échecs: {cv_stats.get('failed_extractions', 0) + cv_stats.get('failed_llm_calls', 0)}")

            db_stats = stats['database_stats']
            print(f"   Base de données:")
            print(f"     • Total traité: {db_stats['total_processed']}")
            print(f"     • Sauvegardé: {db_stats['successful_saves']}")
            print(f"     • Doublons: {db_stats['duplicates_found']}")

            proc_stats = stats['processing_stats']
            print(f"   Traitement global:")
            print(f"     • Fichiers traités: {proc_stats['files_processed']}")
            print(f"     • Parsing réussis: {proc_stats['parsing_successes']}")
            print(f"     • Sauvegardes DB: {proc_stats['database_saves']}")
            print(f"     • Problèmes qualité: {proc_stats['quality_issues']}")

        print(f"\n✅ Commande '{args.command}' terminée avec succès!")

    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        print(f"🔍 Détails: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()