from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from recruitment.models import Candidate, JobOffer
from .matching_service import MatchingService
import json


@api_view(['POST'])
def candidate_matching(request):
    """
    Lance le matching d'un candidat contre toutes les offres actives
    """
    try:
        candidate_id = request.data.get('candidate_id')
        if not candidate_id:
            return Response(
                {'error': 'candidate_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer le candidat
        candidate = get_object_or_404(Candidate, id=candidate_id)

        # Récupérer toutes les offres actives
        active_jobs = JobOffer.objects.filter(is_active=True)

        if not active_jobs.exists():
            return Response({
                'message': 'Aucune offre active trouvée',
                'results': []
            })

        # Initialiser le service de matching
        matching_service = MatchingService()

        # Préparer les données du candidat depuis les champs JSON
        candidate_data = {
            'technical_skills': candidate.technical_skills or [],
            'soft_skills': candidate.soft_skills or [],
            'experience_years': candidate.experience_summary.get('years', 0) if candidate.experience_summary else 0,
            'experience_level': candidate.experience_summary.get('level', '') if candidate.experience_summary else '',
            'education_level': candidate.education_level or '',
            'current_position': candidate.current_position or '',
            'city': candidate.city or ''
        }

        results = []

        # Faire le matching pour chaque offre
        for job in active_jobs:
            try:
                # Préparer les données de l'offre
                job_data = {
                    'required_skills': job.required_skills or [],
                    'preferred_skills': job.preferred_skills or [],
                    'soft_skills': job.soft_skills_required or [],
                    'experience_required': job.experience_required or 0,
                    'education_required': job.education_level or '',
                    'job_title': job.title,
                    'description': job.description or ''
                }

                # Lancer le matching
                matching_result = matching_service.calculate_match_score(
                    candidate_data,
                    job_data
                )

                # Ajouter les informations de l'offre
                matching_result.update({
                    'job_id': job.id,
                    'job_title': job.title,
                    'company': job.company or 'Non spécifié'
                })

                results.append(matching_result)

            except Exception as e:
                print(f"Erreur lors du matching pour l'offre {job.id}: {str(e)}")
                continue

        # Trier par score global décroissant
        results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)

        # Mettre à jour la date de dernier matching du candidat
        from django.utils import timezone
        candidate.last_matching_date = timezone.now()

        # Mettre à jour le score global avec le meilleur score
        if results:
            candidate.global_match_score = results[0].get('overall_score', 0)

        candidate.save()

        return Response({
            'message': f'Matching terminé pour {candidate.full_name}',
            'candidate_id': candidate.id,
            'total_jobs_analyzed': len(results),
            'results': results
        })

    except Exception as e:
        return Response(
            {'error': f'Erreur lors du matching: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
