# ai_engine/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProcessingJob
from .serializers import ProcessingJobSerializer
from ai_engine.services.cv_parser import CVParserService
from ai_engine.services.ocr_service import OCRService

from ai_engine.services.llm_service import LLMService
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import logging
from typing import Dict, List
from ai_engine.services.matching_service import (
    calculate_adaptive_match_score,
    batch_matching_simple,
    rank_candidates_for_tech_company,
    detect_cv_domain,
    analyze_skill_gaps_simple,
    suggest_training_paths,
    model_manager,
    skill_normalizer
)

logger = logging.getLogger(__name__)




class MatchingViews:
    """Vues Django pour le service de matching"""

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def match_single_cv(request):
        """
        API pour matcher un CV contre une offre
        POST /ai_engine/match-cv/
        """
        try:
            data = json.loads(request.body)
            cv_data = data.get('cv_data')
            job_data = data.get('job_data')
            cv_id = data.get('cv_id', 'unknown')

            if not cv_data or not job_data:
                return JsonResponse({
                    'error': 'CV data et job data requis'
                }, status=400)

            # Vérification modèle
            if not model_manager.is_ready():
                return JsonResponse({
                    'error': 'Service de matching non disponible'
                }, status=503)

            result = calculate_adaptive_match_score(cv_data, job_data, cv_id)

            return JsonResponse({
                'success': True,
                'result': result,
                'cv_id': cv_id
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalide'}, status=400)
        except Exception as e:
            logger.error(f"Erreur matching CV: {str(e)}")
            return JsonResponse({
                'error': f'Erreur interne: {str(e)}'
            }, status=500)

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def batch_matching(request):
        """
        API pour traitement par lot de CV
        POST /ai_engine/batch-match/
        """
        try:
            data = json.loads(request.body)
            cv_list = data.get('cv_list', [])
            job_data = data.get('job_data')
            top_k = data.get('top_k', 10)
            prioritize_tech = data.get('prioritize_tech', True)

            if not cv_list or not job_data:
                return JsonResponse({
                    'error': 'cv_list et job_data requis'
                }, status=400)

            if not model_manager.is_ready():
                return JsonResponse({
                    'error': 'Service de matching non disponible'
                }, status=503)

            if prioritize_tech:
                results = rank_candidates_for_tech_company(cv_list, job_data)
            else:
                results = batch_matching_simple(cv_list, job_data, top_k)

            # Statistiques
            scores = [r["score"] for r in results]
            domains = [r["cv_domain"] for r in results]

            stats = {
                'total_processed': len(cv_list),
                'total_qualified': len(results),
                'avg_score': round(sum(scores) / len(scores), 1) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'domain_distribution': {}
            }

            for domain in set(domains):
                stats['domain_distribution'][domain] = domains.count(domain)

            return JsonResponse({
                'success': True,
                'results': results[:top_k],
                'statistics': stats
            })

        except Exception as e:
            logger.error(f"Erreur batch matching: {str(e)}")
            return JsonResponse({
                'error': f'Erreur interne: {str(e)}'
            }, status=500)

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def analyze_gaps(request):
        """
        API pour analyser les écarts de compétences
        POST /ai_engine/analyze-gaps/
        """
        try:
            data = json.loads(request.body)
            cv_data = data.get('cv_data')
            job_data = data.get('job_data')

            if not cv_data or not job_data:
                return JsonResponse({
                    'error': 'cv_data et job_data requis'
                }, status=400)

            gap_analysis = analyze_skill_gaps_simple(cv_data, job_data)
            training_paths = suggest_training_paths(cv_data, job_data)

            return JsonResponse({
                'success': True,
                'gap_analysis': gap_analysis,
                'training_suggestions': training_paths
            })

        except Exception as e:
            logger.error(f"Erreur analyse gaps: {str(e)}")
            return JsonResponse({
                'error': f'Erreur interne: {str(e)}'
            }, status=500)

    @staticmethod
    def testeur_interface(request):
        """
        Interface web pour tester le matching
        GET /ai_engine/testeur/
        """
        context = {
            'title': 'Testeur Service Matching CV',
            'description': 'Interface de test pour le service de matching adaptatif'
        }
        return render(request, 'ai_engine/testeur.html', context)

    @staticmethod
    def health_check(request):
        """
        Vérification santé du service
        GET /ai_engine/health/
        """
        try:
            model_ready = model_manager.is_ready()

            return JsonResponse({
                'status': 'healthy' if model_ready else 'degraded',
                'model_ready': model_ready,
                'cache_size': getattr(model_manager.encode, 'cache_info', lambda: {'currsize': 0})().get('currsize', 0),
                'timestamp': json.dumps(None, default=str)
            })
        except Exception as e:
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e)
            }, status=503)

class AIProcessingViewSet(viewsets.ModelViewSet):
    queryset = ProcessingJob.objects.all()
    serializer_class = ProcessingJobSerializer

    @action(detail=False, methods=['post'])
    def parse_cv(self, request):
        """Endpoint dédié au parsing de CV"""
        try:
            file_path = request.data.get('file_path')
            if not file_path:
                return Response({
                    'success': False,
                    'error': 'Chemin de fichier requis'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Créer job de processing
            processing_job = ProcessingJob.objects.create(
                job_type='cv_parsing',
                status='processing',
                input_data={'file_path': file_path}
            )

            # OCR + Parsing
            ocr_service = OCRService()
            cv_text = ocr_service.process(file_path)

            parser_service = CVParserService()
            parsed_data = parser_service.process(cv_text)

            # Mise à jour job
            processing_job.status = 'completed'
            processing_job.output_data = {
                'cv_text': cv_text,
                'parsed_data': parsed_data
            }
            processing_job.save()

            return Response({
                'success': True,
                'job_id': processing_job.id,
                'result': processing_job.output_data
            })

        except Exception as e:
            logger.error(f"Erreur parsing CV: {e}")
            if 'processing_job' in locals():
                processing_job.status = 'failed'
                processing_job.error_message = str(e)
                processing_job.save()

            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def calculate_matching(self, request):
        """Endpoint pour calcul de matching"""
        try:
            candidate_id = request.data.get('candidate_id')
            job_offer_id = request.data.get('job_offer_id')

            matching_service = MatchingService()
            result = matching_service.process({
                'candidate_id': candidate_id,
                'job_offer_id': job_offer_id
            })

            return Response({
                'success': True,
                'matching_result': result
            })

        except Exception as e:
            logger.error(f"Erreur matching: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def generate_content(self, request):
        """Endpoint pour génération de contenu LLM"""
        try:
            prompt = request.data.get('prompt')
            content_type = request.data.get('type', 'general')  # job_description, questions, etc.

            llm_service = LLMService()

            # Templates spécialisés selon le type
            if content_type == 'job_description':
                enhanced_prompt = f"""
                Génère une description de poste professionnelle en français pour:
                {prompt}

                Structure attendue:
                - Présentation de l'entreprise
                - Mission du poste
                - Responsabilités principales
                - Profil recherché
                - Avantages

                Style: professionnel, attractif, sans discrimination.
                """
            elif content_type == 'interview_questions':
                enhanced_prompt = f"""
                Génère 8 questions d'entretien pertinentes pour:
                {prompt}

                Inclure:
                - 3 questions techniques
                - 3 questions comportementales
                - 2 questions situationnelles

                Questions en français, adaptées au contexte marocain.
                """
            else:
                enhanced_prompt = prompt

            result = llm_service.generate_text(enhanced_prompt)

            return Response({
                'success': True,
                'generated_content': result,
                'content_type': content_type
            })

        except Exception as e:
            logger.error(f"Erreur génération contenu: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

