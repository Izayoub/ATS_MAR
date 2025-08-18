import os
import sys
import django
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# =====================================================
# Initialisation Django
# =====================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ATS_MA.settings")

try:
    django.setup()
    from django.conf import settings
    DJANGO_AVAILABLE = True
except Exception:
    DJANGO_AVAILABLE = False

# =====================================================
# Configuration des logs
# =====================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================================================
# Dataclasses
# =====================================================
@dataclass
class MatchResult:
    """Résultat de matching pour un champ spécifique"""
    field_name: str
    similarity_score: float
    candidate_value: Any
    job_value: Any
    confidence: str  # 'high', 'medium', 'low'


@dataclass
class CandidateJobMatch:
    """Résultat complet de matching entre un candidat et une offre"""
    candidate_id: int
    job_id: int
    overall_score: float
    field_matches: List[MatchResult]
    recommendation: str  # 'excellent', 'good', 'fair', 'poor'


# =====================================================
# Service de Matching
# =====================================================
class MatchingService:
    """Service de matching utilisant Bi-Encoder et Cross-Encoder"""

    def __init__(self,
                 bi_encoder_model: str = "BAAI/bge-m3",
                 cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Utilisation du device: {self.device}")

        try:
            logger.info(f"Chargement du Bi-Encoder: {bi_encoder_model}")
            self.bi_encoder = SentenceTransformer(bi_encoder_model, device=self.device)

            logger.info(f"Chargement du Cross-Encoder: {cross_encoder_model}")
            self.cross_encoder = CrossEncoder(cross_encoder_model, device=self.device)

        except Exception as e:
            logger.error(f"Erreur lors du chargement des modèles: {e}")
            raise

        self.field_weights = {
            'skills': 0.30,
            'experience': 0.25,
            'education': 0.20,
            'location': 0.10,
            'description': 0.15
        }

    # =====================================================
    # Connexion DB
    # =====================================================
    def get_db_connection(self):
        """Établit une connexion à la base de données"""
        try:
            if DJANGO_AVAILABLE and settings.configured and hasattr(settings, "DATABASES"):
                db_config = settings.DATABASES["default"]
                conn = psycopg2.connect(
                    host=db_config.get("HOST", "localhost"),
                    database=db_config.get("NAME", "ATS"),
                    user=db_config.get("USER", "ayoub"),
                    password=db_config.get("PASSWORD", "password"),
                    port=db_config.get("PORT", "5432"),
                )
            else:
                conn = psycopg2.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    database=os.getenv("DB_NAME", "ATS"),
                    user=os.getenv("DB_USER", "ayoub"),
                    password=os.getenv("DB_PASSWORD", "password"),
                    port=os.getenv("DB_PORT", "5432"),
                )
            return conn
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            raise

    # =====================================================
    # Fonctions utilitaires
    # =====================================================
    def extract_skills_from_text(self, text: str) -> List[str]:
        if not text:
            return []
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|React|Angular|Vue|Django|Flask|Node\.js|PHP|Ruby|Go|Rust|C\+\+|C#|Swift|Kotlin|SQL|MongoDB|PostgreSQL|MySQL|Redis|Docker|Kubernetes|AWS|Azure|GCP|Git|Linux|Windows|MacOS|HTML|CSS|TypeScript|jQuery|Bootstrap|Sass|REST|GraphQL|API|Microservices|DevOps|CI/CD|Jenkins|GitLab|GitHub|Jira|Slack|Figma|Photoshop|Illustrator|Sketch|Adobe|Office|Excel|PowerPoint|Word|Project|Scrum|Agile|Kanban|Machine Learning|AI|Data Science|TensorFlow|PyTorch|Pandas|NumPy|Matplotlib|Tableau|Power BI|R|SPSS|Statistics|Analytics)\b'
        ]
        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend([m.lower() for m in matches])
        return list(set(skills))

    def normalize_experience_level(self, level: str) -> int:
        mapping = {
            'junior': 1, 'entry': 1, 'débutant': 1,
            'mid': 3, 'middle': 3, 'intermédiaire': 3,
            'senior': 5, 'lead': 7,
            'principal': 10, 'expert': 10
        }
        return mapping.get(level.lower().strip(), 2)

    # =====================================================
    # Fonctions de Similarité (skills, exp, edu, etc.)
    # =====================================================
    def calculate_skills_similarity(self, candidate_skills: List[str], job_requirements: str) -> MatchResult:
        if not candidate_skills or not job_requirements:
            return MatchResult("skills", 0.0, candidate_skills, job_requirements, "low")

        required_skills = self.extract_skills_from_text(job_requirements)
        if not required_skills:
            return MatchResult("skills", 0.0, candidate_skills, required_skills, "low")

        candidate_text = " ".join(candidate_skills)
        required_text = " ".join(required_skills)

        embeddings = self.bi_encoder.encode([candidate_text, required_text])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        cross_score = self.cross_encoder.predict([(candidate_text, required_text)])[0]
        final_score = (similarity * 0.7 + cross_score * 0.3)

        confidence = "high" if final_score >= 0.7 else "medium" if final_score >= 0.5 else "low"
        return MatchResult("skills", final_score, candidate_skills, required_skills, confidence)

    def calculate_experience_similarity(self, candidate_years: int, job_level: str) -> MatchResult:
        required_years = self.normalize_experience_level(job_level)
        if candidate_years == 0 or required_years == 0:
            return MatchResult("experience", 0.0, candidate_years, required_years, "low")

        diff = abs(candidate_years - required_years)
        if diff == 0:
            score = 1.0
        elif diff <= 1:
            score = 0.8
        elif diff <= 2:
            score = 0.6
        elif diff <= 3:
            score = 0.4
        else:
            score = 0.2

        if candidate_years > required_years:
            score = min(1.0, score + 0.1)

        confidence = "high" if score >= 0.7 else "medium" if score >= 0.5 else "low"
        return MatchResult("experience", score, candidate_years, required_years, confidence)

    def calculate_education_similarity(self, candidate_education: str, job_description: str) -> MatchResult:
        if not candidate_education or not job_description:
            return MatchResult("education", 0.0, candidate_education, "", "low")

        education_keywords = re.findall(
            r'\b(?:bac|licence|master|doctorat|phd|ingénieur|dut|bts|bachelor|degree)\b',
            job_description.lower()
        )
        if not education_keywords:
            return MatchResult("education", 0.5, candidate_education, "Non spécifié", "medium")

        embeddings = self.bi_encoder.encode([candidate_education.lower(), " ".join(education_keywords)])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        cross_score = self.cross_encoder.predict([(candidate_education.lower(), " ".join(education_keywords))])[0]
        final_score = (similarity * 0.6 + cross_score * 0.4)

        confidence = "high" if final_score >= 0.7 else "medium" if final_score >= 0.5 else "low"
        return MatchResult("education", final_score, candidate_education, education_keywords, confidence)

    def calculate_location_similarity(self, candidate_city: str, job_location: str, remote_allowed: bool) -> MatchResult:
        if remote_allowed:
            return MatchResult("location", 1.0, candidate_city, f"{job_location} (Remote)", "high")

        if not candidate_city or not job_location:
            return MatchResult("location", 0.0, candidate_city, job_location, "low")

        cand, job = candidate_city.lower().strip(), job_location.lower().strip()
        if cand == job:
            return MatchResult("location", 1.0, candidate_city, job_location, "high")

        embeddings = self.bi_encoder.encode([cand, job])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        confidence = "high" if similarity >= 0.8 else "medium" if similarity >= 0.6 else "low"
        return MatchResult("location", similarity, candidate_city, job_location, confidence)

    def calculate_description_similarity(self, candidate_summary: str, job_description: str) -> MatchResult:
        if not candidate_summary or not job_description:
            return MatchResult("description", 0.0, candidate_summary, job_description, "low")

        embeddings = self.bi_encoder.encode([candidate_summary, job_description])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        cross_score = self.cross_encoder.predict([(candidate_summary, job_description)])[0]
        final_score = (similarity * 0.6 + cross_score * 0.4)

        confidence = "high" if final_score >= 0.7 else "medium" if final_score >= 0.5 else "low"
        return MatchResult("description", final_score, candidate_summary[:100] + "...", job_description[:100] + "...", confidence)

    # =====================================================
    # Matching principal
    # =====================================================
    def match_candidate_to_job(self, candidate_data: Dict, job_data: Dict) -> CandidateJobMatch:
        logger.info(f"Matching candidat {candidate_data['id']} avec job {job_data['id']}")

        field_matches = []
        candidate_skills = candidate_data.get("skills_extracted", [])
        if isinstance(candidate_skills, str):
            candidate_skills = json.loads(candidate_skills) if candidate_skills else []

        field_matches.append(self.calculate_skills_similarity(candidate_skills, job_data.get("requirements", "")))
        field_matches.append(self.calculate_experience_similarity(candidate_data.get("experience_years", 0), job_data.get("experience_level", "")))
        field_matches.append(self.calculate_education_similarity(candidate_data.get("education_level", ""), job_data.get("description", "") + " " + job_data.get("requirements", "")))
        field_matches.append(self.calculate_location_similarity(candidate_data.get("city", ""), job_data.get("location", ""), job_data.get("remote_allowed", False)))
        field_matches.append(self.calculate_description_similarity(candidate_data.get("ai_summary", ""), job_data.get("description", "")))

        overall_score = sum([m.similarity_score * self.field_weights.get(m.field_name, 0.1) for m in field_matches])
        recommendation = "excellent" if overall_score >= 0.8 else "good" if overall_score >= 0.6 else "fair" if overall_score >= 0.4 else "poor"

        return CandidateJobMatch(candidate_id=candidate_data["id"], job_id=job_data["id"], overall_score=overall_score, field_matches=field_matches, recommendation=recommendation)

    # =====================================================
    # Accès DB
    # =====================================================
    def get_candidates_from_db(self, limit: Optional[int] = None) -> List[Dict]:
        conn = self.get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT id, first_name, last_name, email, phone, gender, birth_date,
                       address, city, linkedin_url, cv_text, cv_parsed_data,
                       skills_extracted, experience_years, education_level,
                       languages, ai_summary, created_at, updated_at
                FROM recruitment_candidate
                """
                if limit:
                    query += f" LIMIT {limit}"
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_job_offers_from_db(self, limit: Optional[int] = None) -> List[Dict]:
        conn = self.get_db_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT j.id, j.title, j.description, j.requirements, j.benefits,
                       j.status, j.experience_level, j.salary_min, j.salary_max,
                       j.location, j.remote_allowed, j.contract_type, j.deadline,
                       j.company_id, c.name as company_name
                FROM recruitment_joboffer j
                JOIN accounts_company c ON j.company_id = c.id
                WHERE j.status = 'active'
                """
                if limit:
                    query += f" LIMIT {limit}"
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # =====================================================
    # Recherche de match
    # =====================================================
    def find_best_matches(self, candidate_id: Optional[int] = None, job_id: Optional[int] = None, top_n: int = 10) -> List[CandidateJobMatch]:
        matches = []

        if candidate_id:
            conn = self.get_db_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT * FROM recruitment_candidate WHERE id = %s", (candidate_id,))
                    candidate = dict(cursor.fetchone())
                jobs = self.get_job_offers_from_db()
                for job in jobs:
                    matches.append(self.match_candidate_to_job(candidate, job))
            finally:
                conn.close()

        elif job_id:
            conn = self.get_db_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT j.*, c.name as company_name 
                        FROM recruitment_joboffer j
                        JOIN accounts_company c ON j.company_id = c.id
                        WHERE j.id = %s
                    """, (job_id,))
                    job = dict(cursor.fetchone())
                candidates = self.get_candidates_from_db()
                for candidate in candidates:
                    matches.append(self.match_candidate_to_job(candidate, job))
            finally:
                conn.close()
        else:
            candidates = self.get_candidates_from_db(limit=50)
            jobs = self.get_job_offers_from_db(limit=20)
            for cand in candidates:
                for job in jobs:
                    matches.append(self.match_candidate_to_job(cand, job))

        matches.sort(key=lambda x: x.overall_score, reverse=True)
        return matches[:top_n]

    def generate_match_report(self, match: CandidateJobMatch) -> str:
        report = f"""
=== RAPPORT DE MATCHING ===
Candidat ID: {match.candidate_id}
Job ID: {match.job_id}
Score Global: {match.overall_score:.3f}
Recommandation: {match.recommendation.upper()}

=== DÉTAIL PAR CHAMP ===
"""
        for field_match in match.field_matches:
            report += f"""
{field_match.field_name.upper()}:
  Score: {field_match.similarity_score:.3f}
  Confiance: {field_match.confidence}
  Candidat: {field_match.candidate_value}
  Job: {field_match.job_value}
"""
        return report


# =====================================================
# Fonction de test
# =====================================================
def run_matching_with_database():
    try:
        matching_service = MatchingService()

        logger.info("=== TEST DE CONNEXION À LA BASE DE DONNÉES ===")

        candidates = matching_service.get_candidates_from_db(limit=5)
        logger.info(f"Trouvé {len(candidates)} candidats")

        jobs = matching_service.get_job_offers_from_db(limit=5)
        logger.info(f"Trouvé {len(jobs)} offres d'emploi")

        if not candidates or not jobs:
            logger.error("Pas assez de données pour le test.")
            return

        logger.info(f"=== MATCHING POUR LE CANDIDAT {candidates[0]['id']} ===")
        matches = matching_service.find_best_matches(candidate_id=candidates[0]['id'], top_n=3)
        for i, match in enumerate(matches, 1):
            print(f"\n=== MATCH #{i} ===")
            print(matching_service.generate_match_report(match))

        logger.info(f"=== MATCHING POUR L'OFFRE {jobs[0]['id']} ===")
        matches = matching_service.find_best_matches(job_id=jobs[0]['id'], top_n=3)
        for i, match in enumerate(matches, 1):
            print(f"\n=== CANDIDAT MATCH #{i} ===")
            print(matching_service.generate_match_report(match))

        logger.info("✓ Test terminé avec succès!")

    except Exception as e:
        logger.error(f"✗ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_matching_with_database()
