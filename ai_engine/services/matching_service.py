# ai_engine/services/matching_service.py - Version avec imports Django lazy
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class FieldMatch:
    """Résultat de matching pour un champ spécifique"""
    field_name: str
    similarity_score: float
    candidate_value: Any
    job_value: Any
    confidence: str


@dataclass
class MatchResult:
    """Résultat complet de matching"""
    candidate_id: int
    job_id: int
    overall_score: float
    field_matches: List[FieldMatch]
    recommendation: str
    confidence_level: str


class MatchingService:
    """Service de matching unifié avec cache DB uniquement"""

    # Configuration des seuils et poids
    SCORE_THRESHOLDS = {
        'excellent': 0.8,
        'good': 0.6,
        'fair': 0.4,
        'poor': 0.0
    }

    FIELD_WEIGHTS = {
        'technical_skills': 0.35,
        'soft_skills': 0.15,
        'experience': 0.30,
        'education': 0.20
    }

    CACHE_EXPIRY_HOURS = 24

    def __init__(self):
        """Initialisation avec singleton pattern pour les modèles ML"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._bi_encoder = None
        self._cross_encoder = None
        logger.info(f"MatchingService initialized on device: {self.device}")

    def _get_django_imports(self):
        """Lazy import des modules Django"""
        from django.core.cache import cache
        from django.utils import timezone
        from django.db import transaction
        from django.db.models import Q, Prefetch
        from recruitment.models import Candidate, JobOffer, MatchingCache, Application

        return {
            'cache': cache,
            'timezone': timezone,
            'transaction': transaction,
            'Q': Q,
            'Prefetch': Prefetch,
            'Candidate': Candidate,
            'JobOffer': JobOffer,
            'MatchingCache': MatchingCache,
            'Application': Application
        }

    @property
    def bi_encoder(self):
        """Lazy loading du bi-encoder"""
        if self._bi_encoder is None:
            self._bi_encoder = SentenceTransformer("BAAI/bge-m3", device=self.device)
        return self._bi_encoder

    @property
    def cross_encoder(self):
        """Lazy loading du cross-encoder"""
        if self._cross_encoder is None:
            self._cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=self.device)
        return self._cross_encoder

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extraction unifiée des compétences"""
        if not text:
            return []

        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|TypeScript|React|Angular|Vue\.?js|Django|Flask|Node\.?js)\b',
            r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Docker|Kubernetes|AWS|Azure|GCP)\b',
            r'\b(?:Git|Linux|REST|GraphQL|API|Microservices|Agile|Scrum)\b',
        ]

        skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend([m.lower().replace('.', '') for m in matches])

        return list(dict.fromkeys(skills))[:20]

    def _calculate_technical_skills_match(self, candidate_skills: List[str],
                                          job_requirements: str) -> FieldMatch:
        """Calcul unifié de matching des compétences techniques"""
        if not candidate_skills or not job_requirements:
            return FieldMatch("technical_skills", 0.0, candidate_skills, [], "low")

        required_skills = self._extract_skills_from_text(job_requirements)
        if not required_skills:
            return FieldMatch("technical_skills", 0.0, candidate_skills, required_skills, "low")

        # Normalisation
        candidate_skills_clean = [skill.lower().strip() for skill in candidate_skills if skill]
        required_skills_clean = [skill.lower().strip() for skill in required_skills if skill]

        # Matching exact
        exact_matches = set(candidate_skills_clean) & set(required_skills_clean)
        exact_score = len(exact_matches) / len(required_skills_clean) if required_skills_clean else 0

        # Similarité sémantique
        try:
            candidate_text = " ".join(candidate_skills_clean)
            required_text = " ".join(required_skills_clean)

            embeddings = self.bi_encoder.encode([candidate_text, required_text])
            semantic_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

            # Score final pondéré
            final_score = exact_score * 0.6 + semantic_score * 0.4

        except Exception as e:
            logger.warning(f"Error calculating technical skills similarity: {e}")
            final_score = exact_score

        # Confidence
        confidence = (
            "high" if len(exact_matches) >= 3 and final_score >= 0.7
            else "medium" if len(exact_matches) >= 1 and final_score >= 0.5
            else "low"
        )

        return FieldMatch("technical_skills", final_score,
                          candidate_skills[:10], required_skills[:10], confidence)

    def _calculate_soft_skills_match(self, candidate_soft_skills: List[str],
                                     job_description: str) -> FieldMatch:
        """Calcul unifié de matching des soft skills"""
        if not candidate_soft_skills:
            return FieldMatch("soft_skills", 0.0, candidate_soft_skills, [], "low")

        soft_keywords = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical', 'creative', 'adaptability', 'time management'
        ]

        job_text = (job_description or "").lower()
        required_soft = [skill for skill in soft_keywords if skill in job_text]

        if not required_soft:
            return FieldMatch("soft_skills", 0.6, candidate_soft_skills, "Non spécifié", "medium")

        # Similarité sémantique
        try:
            candidate_text = " ".join([skill.lower().strip() for skill in candidate_soft_skills])
            required_text = " ".join(required_soft)

            embeddings = self.bi_encoder.encode([candidate_text, required_text])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        except Exception:
            similarity = 0.5

        confidence = "high" if similarity >= 0.7 else "medium" if similarity >= 0.5 else "low"

        return FieldMatch("soft_skills", similarity, candidate_soft_skills,
                          required_soft, confidence)

    def _calculate_experience_match(self, candidate_years: int, job_level: str) -> FieldMatch:
        """Calcul unifié de matching d'expérience"""
        level_mapping = {
            'junior': {'years': 1, 'range': (0, 2)},
            'middle': {'years': 3, 'range': (2, 5)},
            'senior': {'years': 6, 'range': (5, 15)}
        }

        job_level_clean = job_level.lower().strip()
        level_info = level_mapping.get(job_level_clean, {'years': 2, 'range': (0, 5)})

        required_years = level_info['years']
        min_range, max_range = level_info['range']

        if candidate_years == 0:
            return FieldMatch("experience", 0.0, candidate_years,
                              f"{job_level} ({required_years} ans)", "low")

        # Score basé sur la fourchette
        if min_range <= candidate_years <= max_range:
            score = 1.0
            confidence = "high"
        elif candidate_years < min_range:
            diff = min_range - candidate_years
            score = max(0.3, 1.0 - (diff * 0.2))
            confidence = "medium" if diff <= 1 else "low"
        else:
            diff = candidate_years - max_range
            score = max(0.6, 1.0 - (diff * 0.1))
            confidence = "medium" if diff <= 2 else "low"

        return FieldMatch("experience", score, f"{candidate_years} ans",
                          f"{job_level} ({required_years} ans)", confidence)

    def _calculate_education_match(self, candidate_education: str, job_description: str) -> FieldMatch:
        """Calcul unifié de matching éducation"""
        if not candidate_education:
            return FieldMatch("education", 0.0, candidate_education, "", "low")

        education_hierarchy = {
            'doctorat': 8, 'phd': 8, 'master': 5, 'ingénieur': 5,
            'licence': 3, 'bachelor': 3, 'bts': 2, 'dut': 2, 'bac': 0
        }

        # Niveau candidat
        candidate_level = 0
        candidate_lower = candidate_education.lower()
        for edu, level in education_hierarchy.items():
            if edu in candidate_lower:
                candidate_level = max(candidate_level, level)

        # Niveau requis
        job_text = (job_description or "").lower()
        required_level = 0
        education_keywords = []

        for edu, level in education_hierarchy.items():
            if edu in job_text:
                required_level = max(required_level, level)
                education_keywords.append(edu)

        if not education_keywords:
            return FieldMatch("education", 0.6, candidate_education, "Non spécifié", "medium")

        # Score
        if candidate_level == required_level:
            score = 1.0
            confidence = "high"
        elif candidate_level > required_level:
            diff = candidate_level - required_level
            score = min(1.0, 0.8 + (diff * 0.05))
            confidence = "medium"
        else:
            diff = required_level - candidate_level
            score = max(0.2, 1.0 - (diff * 0.15))
            confidence = "medium" if diff <= 2 else "low"

        return FieldMatch("education", score, candidate_education, education_keywords, confidence)

    def match_candidate_to_job(self, candidate, job_offer) -> MatchResult:
        """Méthode principale de matching unifiée"""
        logger.info(f"Matching candidate {candidate.id} with job {job_offer.id}")

        field_matches = []

        # Compétences techniques
        technical_skills = candidate.technical_skills or []
        if isinstance(technical_skills, str):
            technical_skills = json.loads(technical_skills) if technical_skills else []

        field_matches.append(
            self._calculate_technical_skills_match(technical_skills, job_offer.requirements or "")
        )

        # Compétences comportementales
        soft_skills = candidate.soft_skills or []
        if isinstance(soft_skills, str):
            soft_skills = json.loads(soft_skills) if soft_skills else []

        field_matches.append(
            self._calculate_soft_skills_match(soft_skills, job_offer.description or "")
        )

        # Expérience
        field_matches.append(
            self._calculate_experience_match(
                candidate.experience_years or 0,
                job_offer.experience_level or ""
            )
        )

        # Éducation
        field_matches.append(
            self._calculate_education_match(
                candidate.education_level or "",
                f"{job_offer.description or ''} {job_offer.requirements or ''}"
            )
        )

        # Score global
        overall_score = sum([
            match.similarity_score * self.FIELD_WEIGHTS.get(match.field_name, 0.1)
            for match in field_matches
        ])

        # Recommandation
        recommendation = next(
            (level for level, threshold in sorted(self.SCORE_THRESHOLDS.items(),
                                                  key=lambda x: x[1], reverse=True)
             if overall_score >= threshold),
            "poor"
        )

        # Confidence globale
        high_confidence_count = sum(1 for match in field_matches if match.confidence == "high")
        if high_confidence_count >= 3:
            confidence_level = "high"
        elif high_confidence_count >= 1:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return MatchResult(
            candidate_id=candidate.id,
            job_id=job_offer.id,
            overall_score=overall_score,
            field_matches=field_matches,
            recommendation=recommendation,
            confidence_level=confidence_level
        )

    def get_cached_match(self, candidate_id: int, job_id: int) -> Optional[MatchResult]:
        """Récupération depuis le cache DB uniquement"""
        django = self._get_django_imports()

        try:
            cached = django['MatchingCache'].objects.select_related('candidate', 'job_offer').get(
                candidate_id=candidate_id,
                job_offer_id=job_id,
                is_valid=True,
                calculated_at__gt=django['timezone'].now() - timedelta(hours=self.CACHE_EXPIRY_HOURS)
            )

            # Reconstruction du MatchResult
            field_matches = []
            for field_name, data in cached.detailed_scores.items():
                field_matches.append(FieldMatch(
                    field_name=field_name,
                    similarity_score=data['score'],
                    candidate_value=data['candidate_value'],
                    job_value=data['job_value'],
                    confidence=data['confidence']
                ))

            return MatchResult(
                candidate_id=cached.candidate_id,
                job_id=cached.job_offer_id,
                overall_score=cached.overall_score,
                field_matches=field_matches,
                recommendation=cached.recommendation,
                confidence_level=cached.detailed_scores.get('confidence_level', 'medium')
            )

        except django['MatchingCache'].DoesNotExist:
            return None

    def save_match_to_cache(self, match: MatchResult):
        """Sauvegarde dans le cache DB uniquement"""
        django = self._get_django_imports()

        detailed_scores = {}
        for field_match in match.field_matches:
            detailed_scores[field_match.field_name] = {
                'score': field_match.similarity_score,
                'confidence': field_match.confidence,
                'candidate_value': str(field_match.candidate_value)[:500],
                'job_value': str(field_match.job_value)[:500]
            }

        detailed_scores['confidence_level'] = match.confidence_level

        with django['transaction'].atomic():
            django['MatchingCache'].objects.update_or_create(
                candidate_id=match.candidate_id,
                job_offer_id=match.job_id,
                defaults={
                    'overall_score': match.overall_score,
                    'detailed_scores': detailed_scores,
                    'recommendation': match.recommendation,
                    'calculated_at': django['timezone'].now(),
                    'is_valid': True
                }
            )

    def find_matches_for_candidate(self, candidate_id: int,
                                   top_n: int = 10,
                                   min_score: float = 0.0) -> List[MatchResult]:
        """Trouve les meilleurs jobs pour un candidat"""
        django = self._get_django_imports()

        try:
            candidate = django['Candidate'].objects.get(id=candidate_id)
        except django['Candidate'].DoesNotExist:
            logger.error(f"Candidate {candidate_id} not found")
            return []

        # Jobs actifs
        active_jobs = django['JobOffer'].objects.filter(
            status='active'
        ).select_related('company').prefetch_related(
            django['Prefetch']('matchingcache_set',
                               queryset=django['MatchingCache'].objects.filter(candidate_id=candidate_id))
        )

        matches = []
        for job in active_jobs:
            # Vérifier le cache
            cached_match = self.get_cached_match(candidate_id, job.id)

            if cached_match:
                matches.append(cached_match)
            else:
                # Calculer et sauvegarder
                match = self.match_candidate_to_job(candidate, job)
                self.save_match_to_cache(match)
                matches.append(match)

        # Filtrer et trier
        matches = [m for m in matches if m.overall_score >= min_score]
        matches.sort(key=lambda x: x.overall_score, reverse=True)

        return matches[:top_n]

    def find_matches_for_job(self, job_id: int,
                             top_n: int = 10,
                             min_score: float = 0.0) -> List[MatchResult]:
        """Trouve les meilleurs candidats pour un job"""
        django = self._get_django_imports()

        try:
            job = django['JobOffer'].objects.select_related('company').get(id=job_id)
        except django['JobOffer'].DoesNotExist:
            logger.error(f"Job {job_id} not found")
            return []

        # Candidats actifs
        active_candidates = django['Candidate'].objects.filter(
            status__in=['active', 'seeking']
        ).prefetch_related(
            django['Prefetch']('matchingcache_set',
                               queryset=django['MatchingCache'].objects.filter(job_offer_id=job_id))
        )

        matches = []
        for candidate in active_candidates:
            # Vérifier le cache
            cached_match = self.get_cached_match(candidate.id, job_id)

            if cached_match:
                matches.append(cached_match)
            else:
                # Calculer et sauvegarder
                match = self.match_candidate_to_job(candidate, job)
                self.save_match_to_cache(match)
                matches.append(match)

        # Filtrer et trier
        matches = [m for m in matches if m.overall_score >= min_score]
        matches.sort(key=lambda x: x.overall_score, reverse=True)

        return matches[:top_n]

    def quick_match(self, candidate_id: int, job_id: int) -> Optional[MatchResult]:
        """Match rapide entre un candidat et un job"""
        django = self._get_django_imports()

        # Vérifier le cache d'abord
        cached_match = self.get_cached_match(candidate_id, job_id)
        if cached_match:
            return cached_match

        try:
            candidate = django['Candidate'].objects.get(id=candidate_id)
            job = django['JobOffer'].objects.select_related('company').get(id=job_id)

            match = self.match_candidate_to_job(candidate, job)
            self.save_match_to_cache(match)

            return match

        except (django['Candidate'].DoesNotExist, django['JobOffer'].DoesNotExist) as e:
            logger.error(f"Entity not found for quick match: {e}")
            return None

    def invalidate_cache(self, candidate_id: Optional[int] = None,
                         job_id: Optional[int] = None) -> int:
        """Invalide le cache selon les paramètres"""
        django = self._get_django_imports()

        queryset = django['MatchingCache'].objects.all()

        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        if job_id:
            queryset = queryset.filter(job_offer_id=job_id)

        return queryset.update(is_valid=False)


# Instance globale du service (Singleton)
matching_service = MatchingService()