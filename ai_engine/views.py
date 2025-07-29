# ai_engine/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProcessingJob
from .serializers import ProcessingJobSerializer
from ai_engine.services.cv_parser import CVParserService
from ai_engine.services.ocr_service import OCRService
from ai_engine.services.matching_service import MatchingService
from ai_engine.services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)


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

