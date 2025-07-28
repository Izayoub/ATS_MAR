import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings
from .base import BaseAIService
from recruitment.models import Candidate, JobOffer
import logging

logger = logging.getLogger(__name__)


class MatchingService(BaseAIService):
    def __init__(self):
        super().__init__()
        self.model_path = settings.AI_CONFIG.get('BGE_MODEL_PATH')

    def load_model(self):
        try:
            # Charger BGE-M3 pour embedding multilingue
            self.model = SentenceTransformer('BAAI/bge-m3')
            self.is_loaded = True
            logger.info("BGE-M3 model loaded successfully")
        except Exception as e:
            logger.error(f"Erreur chargement BGE-M3: {e}")
            raise

    def create_job_embedding(self, job_offer):
        """Création d'embedding pour une offre d'emploi"""
        job_text = f"""
        {job_offer.title}
        {job_offer.description}
        {job_offer.requirements}
        Niveau: {job_offer.experience_level}
        Localisation: {job_offer.location}
        """

        self.ensure_model_loaded()
        embedding = self.model.encode([job_text])
        return embedding[0]

    def create_candidate_embedding(self, candidate):
        """Création d'embedding pour un candidat"""
        # Construire le texte représentant le candidat
        skills = candidate.skills_extracted
        technical_skills = skills.get('technical_skills', []) if isinstance(skills, dict) else []
        soft_skills = skills.get('soft_skills', []) if isinstance(skills, dict) else []

        candidate_text = f"""
        {candidate.ai_summary}
        Compétences techniques: {', '.join(technical_skills)}
        Compétences transversales: {', '.join(soft_skills)}
        Expérience: {candidate.experience_years} ans
        Localisation: {candidate.city}
        """

        self.ensure_model_loaded()
        embedding = self.model.encode([candidate_text])
        return embedding[0]

    def calculate_similarity(self, embedding1, embedding2):
        """Calcul de similarité cosinus entre deux embeddings"""
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

    def calculate_match_score(self, candidate, job_offer):
        """Calcul du score de matching global"""
        try:
            # 1. Similarité sémantique (40%)
            job_embedding = self.create_job_embedding(job_offer)
            candidate_embedding = self.create_candidate_embedding(candidate)
            semantic_score = self.calculate_similarity(job_embedding, candidate_embedding)

            # 2. Correspondance expérience (30%)
            experience_score = self.calculate_experience_match(candidate, job_offer)

            # 3. Correspondance compétences (20%)
            skills_score = self.calculate_skills_match(candidate, job_offer)

            # 4. Correspondance géographique (10%)
            location_score = self.calculate_location_match(candidate, job_offer)

            # Score total pondéré
            total_score = (
                                  semantic_score * 0.4 +
                                  experience_score * 0.3 +
                                  skills_score * 0.2 +
                                  location_score * 0.1
                          ) * 100

            return {
                'total_score': int(total_score),
                'semantic_score': int(semantic_score * 100),
                'experience_score': int(experience_score * 100),
                'skills_score': int(skills_score * 100),
                'location_score': int(location_score * 100),
                'cultural_fit': int(semantic_score * 100)  # Approximation
            }

        except Exception as e:
            logger.error(f"Erreur calcul matching: {e}")
            return {
                'total_score': 0,
                'semantic_score': 0,
                'experience_score': 0,
                'skills_score': 0,
                'location_score': 0,
                'cultural_fit': 0
            }

    def calculate_experience_match(self, candidate, job_offer):
        """Correspondance niveau d'expérience"""
        candidate_years = candidate.experience_years or 0

        experience_mapping = {
            'junior': (0, 2),
            'middle': (2, 5),
            'senior': (5, 100)
        }

        required_min, required_max = experience_mapping.get(job_offer.experience_level, (0, 100))

        if required_min <= candidate_years <= required_max:
            return 1.0
        elif candidate_years < required_min:
            # Pénalité pour manque d'expérience
            return max(0, candidate_years / required_min)
        else:
            # Léger bonus pour sur-qualification
            return min(1.0, 0.8 + (candidate_years - required_max) * 0.05)

    def calculate_skills_match(self, candidate, job_offer):
        """Correspondance des compétences"""
        try:
            skills = candidate.skills_extracted
            if not isinstance(skills, dict):
                return 0.5

            candidate_skills = skills.get('technical_skills', [])
            if not candidate_skills:
                return 0.3

            # Recherche de mots-clés techniques dans l'offre
            job_text = f"{job_offer.description} {job_offer.requirements}".lower()

            matching_skills = 0
            for skill in candidate_skills:
                if skill.lower() in job_text:
                    matching_skills += 1

            if len(candidate_skills) == 0:
                return 0.3

            return min(1.0, matching_skills / len(candidate_skills))

        except Exception as e:
            logger.error(f"Erreur calcul compétences: {e}")
            return 0.5

    def calculate_location_match(self, candidate, job_offer):
        """Correspondance géographique"""
        if not candidate.city or not job_offer.location:
            return 0.5

        if job_offer.remote_allowed:
            return 1.0

        # Correspondance exacte ville
        if candidate.city.lower() in job_offer.location.lower():
            return 1.0

        # Principales villes marocaines (correspondance régionale)
        city_regions = {
            'casablanca': ['mohammedia', 'berrechid'],
            'rabat': ['sale', 'temara', 'kenitra'],
            'fes': ['meknes'],
            'marrakech': ['essaouira'],
            'tangier': ['tetouan']
        }

        candidate_city = candidate.city.lower()
        job_city = job_offer.location.lower()

        for main_city, nearby_cities in city_regions.items():
            if main_city in candidate_city and main_city in job_city:
                return 1.0
            if candidate_city in nearby_cities and main_city in job_city:
                return 0.8
            if main_city in candidate_city and job_city in nearby_cities:
                return 0.8

        return 0.3  # Villes différentes

    def find_matching_candidates(self, job_offer, limit=10):
        """Recherche des meilleurs candidats pour une offre"""
        try:
            candidates = Candidate.objects.all()
            candidate_scores = []

            for candidate in candidates:
                score_data = self.calculate_match_score(candidate, job_offer)
                candidate_scores.append({
                    'candidate': candidate,
                    'score': score_data['total_score']
                })

            # Trier par score décroissant
            candidate_scores.sort(key=lambda x: x['score'], reverse=True)

            # Retourner les meilleurs candidats
            return [item['candidate'] for item in candidate_scores[:limit]]

        except Exception as e:
            logger.error(f"Erreur recherche candidats: {e}")
            return []

    def process(self, input_data):
        """Interface générique pour le service de matching"""
        candidate_id = input_data.get('candidate_id')
        job_offer_id = input_data.get('job_offer_id')

        candidate = Candidate.objects.get(id=candidate_id)
        job_offer = JobOffer.objects.get(id=job_offer_id)

        return self.calculate_match_score(candidate, job_offer)