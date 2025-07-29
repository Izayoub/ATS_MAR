from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import JobOffer, Candidate, Application, Interview
from .serializers import (
    JobOfferSerializer, CandidateSerializer,
    ApplicationSerializer, InterviewSerializer
)
from ai_engine.services.cv_parser import CVParserService
from ai_engine.services.ocr_service import OCRService
from ai_engine.services.matching_service import MatchingService
import logging

logger = logging.getLogger(__name__)


class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'experience_level', 'location', 'company']

    def get_queryset(self):
        return JobOffer.objects.filter(
            company=self.request.user.company
        ).select_related('company', 'created_by')

    def perform_create(self, serializer):
        serializer.save(
            company=self.request.user.company,
            created_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def generate_questions(self, request, pk=None):
        """Génération de questions d'entretien par IA"""
        job_offer = self.get_object()

        try:
            from ai_engine.services.llm_service import LLMService
            llm_service = LLMService()

            prompt = f"""
            Génère 10 questions d'entretien pour ce poste:

            Titre: {job_offer.title}
            Description: {job_offer.description[:500]}
            Exigences: {job_offer.requirements[:500]}
            Niveau: {job_offer.experience_level}

            Réponds en JSON avec cette structure:
            {{
                "technical_questions": ["Question technique 1", "Question technique 2"],
                "behavioral_questions": ["Question comportementale 1"],
                "situational_questions": ["Question situationnelle 1"]
            }}
            """

            response = llm_service.generate_text(prompt)

            return Response({
                'success': True,
                'questions': response
            })

        except Exception as e:
            logger.error(f"Erreur génération questions: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def matching_candidates(self, request, pk=None):
        """Recherche de candidats compatibles avec l'offre"""
        job_offer = self.get_object()

        try:
            matching_service = MatchingService()
            candidates = matching_service.find_matching_candidates(job_offer)

            serializer = CandidateSerializer(candidates, many=True)
            return Response({
                'success': True,
                'candidates': serializer.data
            })

        except Exception as e:
            logger.error(f"Erreur matching candidats: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = CandidateSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'experience_years']

    def get_queryset(self):
        queryset = Candidate.objects.all()

        # Recherche par compétences
        skills = self.request.query_params.get('skills', None)
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            queryset = queryset.filter(
                skills_extracted__technical_skills__overlap=skill_list
            )

        # Recherche textuelle
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(cv_text__icontains=search) |
                Q(ai_summary__icontains=search)
            )

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['post'])
    def upload_cv(self, request):
        """Upload et parsing automatique de CV"""
        try:
            cv_file = request.FILES.get('cv_file')
            if not cv_file:
                return Response({
                    'success': False,
                    'error': 'Aucun fichier CV fourni'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Créer candidat temporaire
            candidate_data = request.data.copy()
            candidate = Candidate.objects.create(
                first_name=candidate_data.get('first_name', 'Prénom'),
                last_name=candidate_data.get('last_name', 'Nom'),
                email=candidate_data.get('email', f'temp_{cv_file.name}@temp.com'),
                cv_file=cv_file
            )

            # Service OCR pour extraction texte
            ocr_service = OCRService()
            cv_text = ocr_service.process(candidate.cv_file.path)

            # Service parsing pour analyse IA
            parser_service = CVParserService()
            parsed_data = parser_service.process(cv_text)

            # Mise à jour candidat avec données parsées
            candidate.cv_text = cv_text
            candidate.cv_parsed_data = parsed_data
            candidate.skills_extracted = parsed_data.get('skills', {})
            candidate.experience_years = parsed_data.get('experience', {}).get('total_experience_years', 0)
            candidate.ai_summary = parsed_data.get('ai_summary', '')

            # Auto-complétion des champs si possibles
            contact_info = parsed_data.get('contact', {})
            if contact_info.get('email') and '@temp.com' in candidate.email:
                candidate.email = contact_info['email']
            if contact_info.get('phone'):
                candidate.phone = contact_info['phone']
            if contact_info.get('linkedin'):
                candidate.linkedin_url = contact_info['linkedin']

            candidate.save()

            serializer = CandidateSerializer(candidate)
            return Response({
                'success': True,
                'candidate': serializer.data,
                'parsed_data': parsed_data
            })

        except Exception as e:
            logger.error(f"Erreur upload CV: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reparse_cv(self, request, pk=None):
        """Re-parsing d'un CV existant"""
        candidate = self.get_object()

        try:
            if not candidate.cv_file:
                return Response({
                    'success': False,
                    'error': 'Aucun CV à re-parser'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Re-parsing complet
            ocr_service = OCRService()
            cv_text = ocr_service.process(candidate.cv_file.path)

            parser_service = CVParserService()
            parsed_data = parser_service.process(cv_text)

            # Mise à jour
            candidate.cv_text = cv_text
            candidate.cv_parsed_data = parsed_data
            candidate.skills_extracted = parsed_data.get('skills', {})
            candidate.experience_years = parsed_data.get('experience', {}).get('total_experience_years', 0)
            candidate.ai_summary = parsed_data.get('ai_summary', '')
            candidate.save()

            serializer = CandidateSerializer(candidate)
            return Response({
                'success': True,
                'candidate': serializer.data
            })

        except Exception as e:
            logger.error(f"Erreur re-parsing: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job_offer', 'source']

    def get_queryset(self):
        return Application.objects.filter(
            job_offer__company=self.request.user.company
        ).select_related('job_offer', 'candidate').order_by('-applied_at')

    @action(detail=False, methods=['post'])
    def create_application(self, request):
        """Création d'une candidature avec matching automatique"""
        try:
            job_offer_id = request.data.get('job_offer_id')
            candidate_id = request.data.get('candidate_id')

            job_offer = get_object_or_404(JobOffer, id=job_offer_id)
            candidate = get_object_or_404(Candidate, id=candidate_id)

            # Vérifier si candidature existe déjà
            existing = Application.objects.filter(
                job_offer=job_offer,
                candidate=candidate
            ).exists()

            if existing:
                return Response({
                    'success': False,
                    'error': 'Candidature déjà existante'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Calcul du matching score avec IA
            matching_service = MatchingService()
            match_score = matching_service.calculate_match_score(candidate, job_offer)

            # Création candidature
            application = Application.objects.create(
                job_offer=job_offer,
                candidate=candidate,
                cover_letter=request.data.get('cover_letter', ''),
                ai_match_score=match_score.get('total_score', 0),
                cultural_fit_score=match_score.get('cultural_fit', 0),
                source=request.data.get('source', 'Manual')
            )

            serializer = ApplicationSerializer(application)
            return Response({
                'success': True,
                'application': serializer.data,
                'match_analysis': match_score
            })

        except Exception as e:
            logger.error(f"Erreur création candidature: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Mise à jour du statut avec notifications automatiques"""
        application = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Application.STATUS_CHOICES):
            return Response({
                'success': False,
                'error': 'Statut invalide'
            }, status=status.HTTP_400_BAD_REQUEST)

        old_status = application.status
        application.status = new_status
        application.save()

        # TODO: Déclencher notifications email/SMS

        return Response({
            'success': True,
            'message': f'Statut mis à jour: {old_status} → {new_status}'
        })

    @action(detail=False, methods=['get'])
    def pipeline_stats(self, request):
        """Statistiques du pipeline de recrutement"""
        queryset = self.get_queryset()

        stats = {}
        for status_code, status_label in Application.STATUS_CHOICES:
            stats[status_code] = {
                'label': status_label,
                'count': queryset.filter(status=status_code).count()
            }

        return Response({
            'success': True,
            'pipeline_stats': stats,
            'total_applications': queryset.count()
        })


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = InterviewSerializer

    def get_queryset(self):
        return Interview.objects.filter(
            application__job_offer__company=self.request.user.company
        ).select_related('application__candidate', 'application__job_offer', 'interviewer')

    @action(detail=True, methods=['post'])
    def generate_evaluation(self, request, pk=None):
        """Génération d'évaluation automatique post-entretien"""
        interview = self.get_object()

        try:
            from ai_engine.services.llm_service import LLMService
            llm_service = LLMService()

            notes = request.data.get('notes', interview.notes)
            if not notes:
                return Response({
                    'success': False,
                    'error': 'Aucune note d\'entretien fournie'
                }, status=status.HTTP_400_BAD_REQUEST)

            prompt = f"""
            Analyse cette évaluation d'entretien et génère un rapport structuré:

            Poste: {interview.application.job_offer.title}
            Candidat: {interview.application.candidate.first_name} {interview.application.candidate.last_name}
            Notes d'entretien: {notes}

            Réponds en JSON:
            {{
                "strengths": ["Point fort 1", "Point fort 2"],
                "weaknesses": ["Point faible 1"],
                "technical_assessment": "Évaluation technique",
                "cultural_fit": "Évaluation culturelle",
                "recommendation": "Recommandation finale",
                "score": 85
            }}
            """

            evaluation = llm_service.generate_text(prompt)

            # Sauvegarder l'évaluation
            interview.ai_evaluation = evaluation
            interview.notes = notes
            interview.save()

            return Response({
                'success': True,
                'evaluation': evaluation
            })

        except Exception as e:
            logger.error(f"Erreur génération évaluation: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
