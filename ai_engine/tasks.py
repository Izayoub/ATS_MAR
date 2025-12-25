# Créer ai_engine/tasks.py:
from datetime import timezone, timedelta

from celery import shared_task
from django.core.cache import cache
import logging

from django.shortcuts import get_object_or_404
from httpcore import Response

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from ai_engine.services.matching_service import MatchingService
from recruitment.models import Candidate

logger = logging.getLogger(__name__)

@shared_task
def run_matching_task(candidate_id, options=None):
    """Tâche Celery pour le matching en arrière-plan"""
    try:
        matching_service = MatchingService()
        matches = matching_service.find_best_matches(
            candidate_id=candidate_id,
            top_n=options.get('maxResults', 10) if options else 10
        )

        # Sauvegarder les résultats en cache ou DB
        cache_key = f"matching_results_{candidate_id}"
        from django.core.cache import cache
        cache.set(cache_key, {
            'status': 'completed',
            'matches': [
                {
                    'job_id': match.job_id,
                    'job_title': 'Titre du job',  # À récupérer depuis la DB
                    'company_name': 'Nom entreprise',
                    'overall_score': match.overall_score,
                    'recommendation': match.recommendation,
                    'field_matches': [
                        {
                            'field_name': fm.field_name,
                            'similarity_score': fm.similarity_score,
                            'confidence': fm.confidence
                        } for fm in match.field_matches
                    ]
                } for match in matches
            ]
        }, timeout=3600)  # 1 heure

        return {'status': 'completed', 'matches_count': len(matches)}

    except Exception as e:
        logger.error(f"Erreur matching candidat {candidate_id}: {e}")
        cache_key = f"matching_results_{candidate_id}"
        from django.core.cache import cache
        cache.set(cache_key, {
            'status': 'error',
            'error': str(e)
        }, timeout=3600)
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_candidate_matching(request, candidate_id):
    """Démarrer le matching pour un candidat"""
    try:
        candidate = get_object_or_404(Candidate, id=candidate_id)

        # Options de matching depuis la requête
        options = {
            'maxResults': request.data.get('maxResults', 10),
            'jobTypes': request.data.get('jobTypes', []),
            'departments': request.data.get('departments', [])
        }

        # Lancer la tâche en arrière-plan
        task = run_matching_task.delay(candidate_id, options)

        # Marquer le matching comme en cours
        cache_key = f"matching_results_{candidate_id}"
        from django.core.cache import cache
        cache.set(cache_key, {
            'status': 'processing',
            'task_id': task.id
        }, timeout=3600)

        return Response({
            'status': 'started',
            'task_id': task.id,
            'message': 'Matching démarré en arrière-plan'
        }, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        logger.error(f"Erreur démarrage matching: {e}")
        return Response({
            'error': 'Erreur lors du démarrage du matching'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@shared_task(bind=True)
def calculate_bulk_matching(self, candidate_ids, job_id, options=None):
    """Calcul de matching en lot pour optimisation"""
    try:
        from recruitment.models import Candidate, JobOffer
        from ai_engine.services.matching_service import MatchingService

        matching_service = MatchingService()
        job_offer = JobOffer.objects.get(id=job_id)

        results = []
        processed = 0
        total = len(candidate_ids)

        for candidate_id in candidate_ids:
            try:
                candidate = Candidate.objects.get(id=candidate_id)

                candidate_data = {
                    'id': candidate.id,
                    'skills_extracted': candidate.skills_extracted,
                    'experience_years': candidate.experience_years or 0,
                    'education_level': candidate.education_level or '',
                    'city': candidate.city or '',
                    'ai_summary': candidate.ai_summary or ''
                }

                job_data = {
                    'id': job_offer.id,
                    'requirements': job_offer.requirements or '',
                    'description': job_offer.description or '',
                    'experience_level': job_offer.experience_level or '',
                    'location': job_offer.location or '',
                    'remote_allowed': job_offer.remote_allowed
                }

                match_result = matching_service.match_candidate_to_job(candidate_data, job_data)

                results.append({
                    'candidate_id': candidate.id,
                    'score': round(match_result.overall_score * 100, 1),
                    'recommendation': match_result.recommendation
                })

                processed += 1

                # Mettre à jour le progrès
                self.update_state(
                    state='PROGRESS',
                    meta={'current': processed, 'total': total}
                )

            except Exception as e:
                logger.error(f"Erreur matching candidat {candidate_id}: {e}")
                continue

        # Sauvegarder en cache
        cache_key = f"bulk_matching_{job_id}_{hash(tuple(candidate_ids))}"
        cache.set(cache_key, {
            'status': 'completed',
            'results': results,
            'job_id': job_id,
            'processed_count': processed
        }, timeout=3600)

        return {
            'status': 'SUCCESS',
            'results_count': len(results),
            'cache_key': cache_key
        }

    except Exception as e:
        logger.error(f"Erreur tâche bulk matching: {e}")
        return {
            'status': 'FAILURE',
            'error': str(e)
        }


@shared_task
def update_matching_cache():
    """Tâche périodique pour mettre à jour le cache de matching"""
    try:
        from recruitment.models import Candidate, JobOffer, MatchingCache

        # Invalider les anciens caches
        MatchingCache.objects.filter(calculated_at__lt=timezone.now() - timedelta(hours=24)).update(is_valid=False)

        # Recalculer pour les combinaisons les plus importantes
        active_jobs = JobOffer.objects.filter(status='active')[:10]
        recent_candidates = Candidate.objects.order_by('-created_at')[:20]

        matching_service = MatchingService()
        updated_count = 0

        for job in active_jobs:
            for candidate in recent_candidates:
                # Vérifier si cache existe et est valide
                cache_entry, created = MatchingCache.objects.get_or_create(
                    candidate=candidate,
                    job_offer=job,
                    defaults={'overall_score': 0, 'detailed_scores': {}, 'recommendation': 'pending'}
                )

                if created or not cache_entry.is_valid:
                    # Recalculer
                    candidate_data = {
                        'id': candidate.id,
                        'skills_extracted': candidate.skills_extracted,
                        'experience_years': candidate.experience_years or 0,
                        'education_level': candidate.education_level or '',
                        'city': candidate.city or '',
                        'ai_summary': candidate.ai_summary or ''
                    }

                    job_data = {
                        'id': job.id,
                        'requirements': job.requirements or '',
                        'description': job.description or '',
                        'experience_level': job.experience_level or '',
                        'location': job.location or '',
                        'remote_allowed': job.remote_allowed
                    }

                    match_result = matching_service.match_candidate_to_job(candidate_data, job_data)

                    cache_entry.overall_score = match_result.overall_score
                    cache_entry.detailed_scores = {
                        fm.field_name: fm.similarity_score for fm in match_result.field_matches
                    }
                    cache_entry.recommendation = match_result.recommendation
                    cache_entry.is_valid = True
                    cache_entry.save()

                    updated_count += 1

        return f"Cache mis à jour: {updated_count} entrées"

    except Exception as e:
        logger.error(f"Erreur mise à jour cache: {e}")
        return f"Erreur: {str(e)}"
