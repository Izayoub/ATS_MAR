# ================================
# recruitment/views.py - Enhanced with AI Matching
# ================================

import json
import sys
import os
from datetime import datetime, timedelta
from collections import Counter

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q, Count, Avg
from django.core.cache import cache
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from sympy.ntheory import qs

from accounts.models import Company
from .forms import JobOfferForm, CompanyForm
from .models import JobOffer, Candidate, Application, Interview, CandidateNote
from .serializers import (
    JobOfferSerializer, CandidateSerializer,
    ApplicationSerializer, InterviewSerializer, CandidateDetailSerializer, CandidateNoteSerializer
)
from ai_engine.services.cv_parser import CVParser
from ai_engine.services.ocr_service import PDFExtractor

# Import du service de matching
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_engine', 'services'))
from ai_engine.services.matching_service import MatchingService
from ai_engine.tasks import run_matching_task

import logging

logger = logging.getLogger(__name__)


# ================================
# CORRECTED CandidateViewSet
# ================================
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['city', 'experience_years', 'education_level']

    def get_queryset(self):
        queryset = Candidate.objects.all()

        # Skills filter
        skills = self.request.query_params.get('skills')
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            queryset = queryset.filter(
                skills_extracted__technical_skills__overlap=skill_list
            )

        # Text search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(cv_text__icontains=search) |
                Q(ai_summary__icontains=search)
            )

        return queryset.order_by('-created_at')

    # =======================
    # Matching: candidats → jobs
    # =======================
    @action(detail=True, methods=['post'])
    def find_matching_jobs(self, request, pk=None):
        """Trouver les meilleurs jobs pour un candidat (synchrone)"""
        candidate = self.get_object()
        matching_service = MatchingService()

        candidate_data = {
            'id': candidate.id,
            'skills_extracted': candidate.skills_extracted,
            'experience_years': candidate.experience_years or 0,
            'education_level': candidate.education_level or '',
            'city': candidate.city or '',
            'ai_summary': candidate.ai_summary or ''
        }

        active_jobs = JobOffer.objects.filter(status='active').select_related('company')
        matches = []

        for job in active_jobs:
            job_data = {
                'id': job.id,
                'title': job.title,
                'requirements': job.requirements or '',
                'description': job.description or '',
                'experience_level': job.experience_level or '',
                'location': job.location or '',
                'remote_allowed': job.remote_allowed,
                'company_name': job.company.name if job.company else 'N/A'
            }

            match_result = matching_service.match_candidate_to_job(candidate_data, job_data)
            matches.append({
                'job_id': job.id,
                'job_title': job.title,
                'company_name': job_data['company_name'],
                'location': job.location,
                'contract_type': job.contract_type,
                'salary_range': f"{job.salary_min or 'N/A'} - {job.salary_max or 'N/A'}",
                'overall_score': round(match_result.overall_score * 100, 1),
                'recommendation': match_result.recommendation,
                'breakdown': {
                    fm.field_name: {
                        'score': round(fm.similarity_score * 100, 1),
                        'confidence': fm.confidence
                    } for fm in match_result.field_matches
                }
            })

        matches.sort(key=lambda x: x['overall_score'], reverse=True)
        return Response({'matches': matches[:10]}, status=200)

    @action(detail=True, methods=['post'])
    def start_async_matching(self, request, pk=None):
        """Démarrer le matching en tâche Celery"""
        candidate = self.get_object()
        options = {
            'maxResults': request.data.get('maxResults', 10)
        }
        task = run_matching_task.delay(candidate.id, options)
        cache.set(f"matching_results_{candidate.id}", {
            'status': 'processing',
            'task_id': task.id
        }, timeout=3600)
        return Response({'status': 'started', 'task_id': task.id}, status=202)

    def get_serializer_class(self):
        """Utiliser serializer détaillé pour retrieve"""
        if self.action == 'retrieve':
            return CandidateDetailSerializer
        return CandidateSerializer

    @action(detail=True, methods=['get', 'post'])
    def notes(self, request, pk=None):
        """Gérer les notes d'un candidat"""
        candidate = self.get_object()

        if request.method == 'GET':
            notes = CandidateNote.objects.filter(candidate=candidate)
            serializer = CandidateNoteSerializer(notes, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CandidateNoteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(candidate=candidate, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Construire la timeline d'un candidat"""
        candidate = self.get_object()
        timeline_events = []

        # Ajouter création du candidat
        timeline_events.append({
            'id': f'created_{candidate.id}',
            'type': 'application',
            'title': 'Candidat créé',
            'description': f'Profil de {candidate.full_name} ajouté au système',
            'date': candidate.created_at.isoformat(),
            'author': 'Système'
        })

        # Ajouter les candidatures
        applications = Application.objects.filter(candidate=candidate).select_related('job_offer', 'job_offer__company')
        for app in applications:
            timeline_events.append({
                'id': f'app_{app.id}',
                'type': 'application',
                'title': f'Candidature envoyée',
                'description': f'Candidature pour {app.job_offer.title} chez {app.job_offer.company.name}',
                'date': app.applied_at.isoformat(),
                'author': candidate.full_name
            })

            if app.last_updated != app.applied_at:
                timeline_events.append({
                    'id': f'app_update_{app.id}',
                    'type': 'status_change',
                    'title': f'Statut mis à jour',
                    'description': f'Candidature {app.job_offer.title} - {app.get_status_display()}',
                    'date': app.last_updated.isoformat(),
                    'author': 'Système'
                })

        # Ajouter les notes
        notes = CandidateNote.objects.filter(candidate=candidate).select_related('author')
        for note in notes:
            timeline_events.append({
                'id': f'note_{note.id}',
                'type': note.note_type,
                'title': f'Note ajoutée',
                'description': note.content[:100] + ('...' if len(note.content) > 100 else ''),
                'date': note.created_at.isoformat(),
                'author': note.author.get_full_name()
            })

        # Trier par date décroissante
        timeline_events.sort(key=lambda x: x['date'], reverse=True)

        return Response(timeline_events)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Mettre à jour le statut d'un candidat"""
        candidate = self.get_object()
        new_status = request.data.get('status')

        if new_status not in [choice[0] for choice in Candidate.STATUS_CHOICES]:
            return Response(
                {'error': 'Statut invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = candidate.status
        candidate.status = new_status
        candidate.save()

        # Ajouter événement timeline
        if old_status != new_status:
            CandidateNote.objects.create(
                candidate=candidate,
                content=f'Statut changé de "{candidate.get_status_display()}" à "{new_status}"',
                note_type='note',
                author=request.user
            )

        serializer = self.get_serializer(candidate)
        return Response(serializer.data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def real_time_matching_stats(request):
    """Real-time matching statistics"""
    try:
        # General stats
        total_candidates = Candidate.objects.count()
        total_active_jobs = JobOffer.objects.filter(status='active').count()
        total_applications = Application.objects.count()

        # Score distribution from existing applications
        score_ranges = {
            'excellent': Application.objects.filter(ai_match_score__gte=80).count(),
            'good': Application.objects.filter(ai_match_score__gte=60, ai_match_score__lt=80).count(),
            'fair': Application.objects.filter(ai_match_score__gte=40, ai_match_score__lt=60).count(),
            'poor': Application.objects.filter(ai_match_score__lt=40).count()
        }

        # Most requested skills
        all_skills = []
        for candidate in Candidate.objects.exclude(skills_extracted__isnull=True):
            if isinstance(candidate.skills_extracted, dict):
                technical_skills = candidate.skills_extracted.get('technical_skills', [])
                if isinstance(technical_skills, list):
                    all_skills.extend(technical_skills)

        top_skills = dict(Counter(all_skills).most_common(10))

        # Matching performance
        recent_applications = Application.objects.filter(
            applied_at__gte=timezone.now() - timedelta(days=7)
        )

        avg_match_score = recent_applications.aggregate(
            avg_score=Avg('ai_match_score')
        )['avg_score'] or 0

        return Response({
            'success': True,
            'stats': {
                'overview': {
                    'total_candidates': total_candidates,
                    'total_active_jobs': total_active_jobs,
                    'total_applications': total_applications,
                    'matching_potential': total_candidates * total_active_jobs
                },
                'score_distribution': score_ranges,
                'top_skills': top_skills,
                'performance': {
                    'avg_match_score_7d': round(avg_match_score, 1),
                    'recent_applications': recent_applications.count(),
                    'conversion_rate': round((recent_applications.count() / max(total_candidates, 1)) * 100, 2)
                }
            },
            'generated_at': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Real-time stats error: {e}")
        return Response({
            'success': False,
            'error': 'Error calculating statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def debug_matching(request):
    """Debug endpoint for testing matching"""
    try:
        candidate_id = request.data.get('candidate_id')
        job_id = request.data.get('job_id')

        if not candidate_id or not job_id:
            return Response({
                'error': 'candidate_id and job_id required'
            }, status=status.HTTP_400_BAD_REQUEST)

        candidate = get_object_or_404(Candidate, id=candidate_id)
        job_offer = get_object_or_404(JobOffer, id=job_id)

        matching_service = MatchingService()

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

        return Response({
            'success': True,
            'debug_info': {
                'candidate_data': candidate_data,
                'job_data': job_data,
                'match_result': {
                    'overall_score': match_result.overall_score,
                    'recommendation': match_result.recommendation,
                    'field_matches': [
                        {
                            'field': fm.field_name,
                            'score': fm.similarity_score,
                            'confidence': fm.confidence,
                            'candidate_value': str(fm.candidate_value)[:200],
                            'job_value': str(fm.job_value)[:200]
                        } for fm in match_result.field_matches
                    ]
                }
            }
        })

    except Exception as e:
        logger.error(f"Debug matching error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# ADDITIONAL VIEWSETS (ApplicationViewSet, InterviewViewSet)
# ================================

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job_offer', 'candidate']

    def get_queryset(self):
        return Application.objects.filter(
            job_offer__company=self.request.user.company
        ).select_related('candidate', 'job_offer', 'job_offer__company')

    @action(detail=True, methods=['post'])
    def update_matching_score(self, request, pk=None):
        """Recalculate matching score for an application"""
        application = self.get_object()

        try:
            matching_service = MatchingService()

            candidate_data = {
                'id': application.candidate.id,
                'skills_extracted': application.candidate.skills_extracted,
                'experience_years': application.candidate.experience_years or 0,
                'education_level': application.candidate.education_level or '',
                'city': application.candidate.city or '',
                'ai_summary': application.candidate.ai_summary or ''
            }

            job_data = {
                'id': application.job_offer.id,
                'requirements': application.job_offer.requirements or '',
                'description': application.job_offer.description or '',
                'experience_level': application.job_offer.experience_level or '',
                'location': application.job_offer.location or '',
                'remote_allowed': application.job_offer.remote_allowed
            }

            match_result = matching_service.match_candidate_to_job(candidate_data, job_data)

            # Update application
            application.ai_match_score = int(match_result.overall_score * 100)
            application.ai_analysis = {
                'recommendation': match_result.recommendation,
                'breakdown': {
                    fm.field_name: fm.similarity_score for fm in match_result.field_matches
                },
                'last_updated': datetime.now().isoformat()
            }
            application.save()

            return Response({
                'success': True,
                'new_score': application.ai_match_score,
                'recommendation': match_result.recommendation
            })

        except Exception as e:
            logger.error(f"Error updating matching score: {e}")
            return Response({
                'success': False,
                'error': 'Error updating matching score'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'interview_type', 'application']

    def get_queryset(self):
        return Interview.objects.filter(
            application__job_offer__company=self.request.user.company
        ).select_related('application', 'application__candidate', 'application__job_offer')

    @action(detail=True, methods=['post'])
    def ai_interview_prep(self, request, pk=None):
        """Generate AI-powered interview preparation suggestions"""
        interview = self.get_object()

        try:
            candidate = interview.application.candidate
            job_offer = interview.application.job_offer

            # Use matching service to identify key areas to focus on
            matching_service = MatchingService()

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

            # Generate interview suggestions based on matching analysis
            suggestions = {
                'strengths_to_highlight': [],
                'areas_to_explore': [],
                'potential_concerns': [],
                'recommended_questions': []
            }

            for field_match in match_result.field_matches:
                score = field_match.similarity_score
                field_name = field_match.field_name

                if score >= 0.8:
                    suggestions['strengths_to_highlight'].append({
                        'area': field_name,
                        'score': round(score * 100, 1),
                        'note': f"Strong match in {field_name}"
                    })
                elif score <= 0.4:
                    suggestions['areas_to_explore'].append({
                        'area': field_name,
                        'score': round(score * 100, 1),
                        'note': f"Potential gap in {field_name} - explore further"
                    })

            # Sample questions based on job requirements
            if job_offer.requirements:
                suggestions['recommended_questions'] = [
                    f"Can you tell us about your experience with {skill}?"
                    for skill in candidate.skills_extracted.get('technical_skills', [])[:3]
                    if isinstance(candidate.skills_extracted, dict)
                ]

            return Response({
                'success': True,
                'interview_prep': suggestions,
                'overall_match_score': round(match_result.overall_score * 100, 1),
                'recommendation': match_result.recommendation
            })

        except Exception as e:
            logger.error(f"Error generating interview prep: {e}")
            return Response({
                'success': False,
                'error': 'Error generating interview preparation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# ADDITIONAL UTILITY FUNCTIONS
# ================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_candidate_scoring(request):
    """Score multiple candidates against a job offer in batch"""
    try:
        job_id = request.data.get('job_id')
        candidate_ids = request.data.get('candidate_ids', [])

        if not job_id or not candidate_ids:
            return Response({
                'success': False,
                'error': 'Job ID and candidate IDs required'
            }, status=status.HTTP_400_BAD_REQUEST)

        job_offer = get_object_or_404(JobOffer, id=job_id)
        matching_service = MatchingService()

        job_data = {
            'id': job_offer.id,
            'requirements': job_offer.requirements or '',
            'description': job_offer.description or '',
            'experience_level': job_offer.experience_level or '',
            'location': job_offer.location or '',
            'remote_allowed': job_offer.remote_allowed
        }

        results = []
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

                match_result = matching_service.match_candidate_to_job(candidate_data, job_data)

                results.append({
                    'candidate_id': candidate.id,
                    'candidate_name': f"{candidate.first_name} {candidate.last_name}",
                    'score': round(match_result.overall_score * 100, 1),
                    'recommendation': match_result.recommendation,
                    'processing_time': 'instant'  # For monitoring
                })

            except Candidate.DoesNotExist:
                results.append({
                    'candidate_id': candidate_id,
                    'error': 'Candidate not found'
                })
                continue

        return Response({
            'success': True,
            'job_title': job_offer.title,
            'results': sorted(results, key=lambda x: x.get('score', 0), reverse=True),
            'processed_count': len([r for r in results if 'score' in r])
        })

    except Exception as e:
        logger.error(f"Batch scoring error: {e}")
        return Response({
            'success': False,
            'error': 'Error during batch scoring'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def matching_analytics_dashboard(request):
    """Comprehensive analytics for matching performance"""
    try:
        # Time range filter
        days_back = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days_back)

        # Applications analytics
        applications = Application.objects.filter(applied_at__gte=start_date)

        # Score trends over time
        score_trends = []
        for i in range(days_back, 0, -1):
            date = timezone.now() - timedelta(days=i)
            day_applications = applications.filter(
                applied_at__date=date.date()
            )
            avg_score = day_applications.aggregate(avg=Avg('ai_match_score'))['avg'] or 0

            score_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'avg_score': round(avg_score, 1),
                'application_count': day_applications.count()
            })

        # Top performing job offers
        job_performance = []
        for job in JobOffer.objects.filter(status='active'):
            job_applications = applications.filter(job_offer=job)
            if job_applications.exists():
                avg_score = job_applications.aggregate(avg=Avg('ai_match_score'))['avg']
                job_performance.append({
                    'job_id': job.id,
                    'job_title': job.title,
                    'company': job.company.name if job.company else 'N/A',
                    'avg_matching_score': round(avg_score, 1),
                    'application_count': job_applications.count()
                })

        job_performance.sort(key=lambda x: x['avg_matching_score'], reverse=True)

        # Skills gap analysis
        skills_gaps = []
        for job in JobOffer.objects.filter(status='active')[:10]:
            job_apps = applications.filter(job_offer=job)
            if job_apps.exists():
                avg_score = job_apps.aggregate(avg=Avg('ai_match_score'))['avg']
                if avg_score < 60:  # Low matching jobs
                    skills_gaps.append({
                        'job_title': job.title,
                        'avg_score': round(avg_score, 1),
                        'required_skills': job.requirements[:200] if job.requirements else 'N/A'
                    })

        return Response({
            'success': True,
            'analytics': {
                'time_range': f'{days_back} days',
                'score_trends': score_trends,
                'top_jobs': job_performance[:10],
                'skills_gaps': skills_gaps,
                'summary': {
                    'total_applications': applications.count(),
                    'avg_score_period': round(applications.aggregate(avg=Avg('ai_match_score'))['avg'] or 0, 1),
                    'high_quality_matches': applications.filter(ai_match_score__gte=80).count(),
                    'improvement_opportunities': len(skills_gaps)
                }
            }
        })

    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        return Response({
            'success': False,
            'error': 'Error generating analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# EXISTING HTML VIEWS (unchanged)
# ================================

@login_required
def joboffer_list(request):
    """List all job offers"""
    joboffers = JobOffer.objects.filter(company=request.user.company)
    return render(request, 'recruitment/joboffer_list.html', {'joboffers': joboffers})


@login_required
def joboffer_detail(request, pk):
    """Job offer detail view"""
    joboffer = get_object_or_404(JobOffer, pk=pk, company=request.user.company)
    return render(request, 'recruitment/joboffer_detail.html', {'joboffer': joboffer})


@login_required
def joboffer_create(request):
    """Create new job offer"""
    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            joboffer = form.save(commit=False)
            joboffer.company = request.user.company
            joboffer.created_by = request.user
            joboffer.save()
            return redirect('joboffer_detail', pk=joboffer.pk)
    else:
        form = JobOfferForm()
    return render(request, 'recruitment/joboffer_form.html', {'form': form})


@login_required
def joboffer_update(request, pk):
    """Update job offer"""
    joboffer = get_object_or_404(JobOffer, pk=pk, company=request.user.company)
    if request.method == 'POST':
        form = JobOfferForm(request.POST, instance=joboffer)
        if form.is_valid():
            form.save()
            return redirect('joboffer_detail', pk=joboffer.pk)
    else:
        form = JobOfferForm(instance=joboffer)
    return render(request, 'recruitment/joboffer_form.html', {'form': form, 'joboffer': joboffer})


@login_required
def joboffer_delete(request, pk):
    """Delete job offer"""
    joboffer = get_object_or_404(JobOffer, pk=pk, company=request.user.company)
    if request.method == 'POST':
        joboffer.delete()
        return redirect('joboffer_list')
    return render(request, 'recruitment/joboffer_confirm_delete.html', {'joboffer': joboffer})


@login_required
def company_list(request):
    """List companies"""
    companies = Company.objects.all()
    return render(request, 'recruitment/company_list.html', {'companies': companies})


@login_required
def company_create(request):
    """Create new company"""
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list')
    else:
        form = CompanyForm()
    return render(request, 'recruitment/company_form.html', {'form': form})


@login_required
def company_detail(request, pk):
    """Company detail view"""
    company = get_object_or_404(Company, pk=pk)
    return render(request, 'recruitment/company_detail.html', {'company': company})


@login_required
def company_update(request, pk):
    """Update company"""
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'recruitment/company_form.html', {'form': form, 'company': company})({
        'success': True,

    })





@action(detail=False, methods=['post'])
def bulk_matching_analysis(self, request):
    """Bulk matching analysis for multiple candidates"""
    try:
        candidate_ids = request.data.get('candidate_ids', [])
        job_id = request.data.get('job_id')

        if not job_id:
            return Response({
                'success': False,
                'error': 'Job offer ID required'
            }, status=status.HTTP_400_BAD_REQUEST)

        job_offer = get_object_or_404(JobOffer, id=job_id)
        matching_service = MatchingService()

        results = []
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
                    'candidate_name': f"{candidate.first_name} {candidate.last_name}",
                    'email': candidate.email,
                    'overall_score': round(match_result.overall_score * 100, 1),
                    'recommendation': match_result.recommendation,
                    'breakdown': {
                        fm.field_name: round(fm.similarity_score * 100, 1)
                        for fm in match_result.field_matches
                    }
                })

            except Candidate.DoesNotExist:
                continue

        # Sort by score
        results.sort(key=lambda x: x['overall_score'], reverse=True)

        return Response({
            'success': True,
            'job_title': job_offer.title,
            'analyzed_candidates': len(results),
            'matches': results
        })

    except Exception as e:
        logger.error(f"Error in bulk matching: {e}")
        return Response({
            'success': False,
            'error': 'Error during bulk analysis'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@action(detail=False, methods=['post'])
def upload_cv(self, request):
    """CV upload with automatic parsing and instant matching"""
    try:
        cv_file = request.FILES.get('cv_file')
        if not cv_file:
            return Response({
                'success': False,
                'error': 'No CV file provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create temporary candidate
        candidate_data = request.data.copy()
        candidate = Candidate.objects.create(
            first_name=candidate_data.get('first_name', 'FirstName'),
            last_name=candidate_data.get('last_name', 'LastName'),
            email=candidate_data.get('email', f'temp_{cv_file.name}@temp.com'),
            cv_file=cv_file
        )

        # OCR service for text extraction
        ocr_service = PDFExtractor()
        cv_text = ocr_service.process(candidate.cv_file.path)

        # Parsing service for AI analysis
        parser_service = CVParser()
        parsed_data = parser_service.process(cv_text)

        # Update candidate with parsed data
        candidate.cv_text = cv_text
        candidate.cv_parsed_data = parsed_data
        candidate.skills_extracted = parsed_data.get('skills', {})
        candidate.experience_years = parsed_data.get('experience', {}).get('total_experience_years', 0)
        candidate.ai_summary = parsed_data.get('ai_summary', '')

        # Auto-complete fields if possible
        contact_info = parsed_data.get('contact', {})
        if contact_info.get('email') and '@temp.com' in candidate.email:
            candidate.email = contact_info['email']
        if contact_info.get('phone'):
            candidate.phone = contact_info['phone']
        if contact_info.get('linkedin'):
            candidate.linkedin_url = contact_info['linkedin']

        candidate.save()

        # NEW: Automatic matching after upload
        matching_jobs = []
        try:
            matching_service = MatchingService()
            matches = matching_service.find_best_matches(candidate_id=candidate.id, top_n=5)

            for match in matches:
                try:
                    job = JobOffer.objects.select_related('company').get(id=match.job_id)
                    matching_jobs.append({
                        'job_id': job.id,
                        'job_title': job.title,
                        'company_name': job.company.name if job.company else 'N/A',
                        'score': round(match.overall_score * 100, 1),
                        'recommendation': match.recommendation
                    })
                except JobOffer.DoesNotExist:
                    continue

        except Exception as e:
            logger.warning(f"Automatic matching failed: {e}")

        serializer = CandidateSerializer(candidate)
        return Response({
            'success': True,
            'candidate': serializer.data,
            'parsed_data': parsed_data,
            'suggested_jobs': matching_jobs
        })

    except Exception as e:
        logger.error(f"CV upload error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================================
# Enhanced JobOfferViewSet
# ================================
class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'experience_level', 'location', 'company']

    def get_queryset(self):
        base_qs = JobOffer.objects.filter(
            company=self.request.user.company
        ).select_related('company', 'created_by')

        if self.action == "list":
            return base_qs.filter(status="active")
        return base_qs

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            company=self.request.user.company
        )

    def perform_update(self, serializer):
        serializer.save(
            company=self.request.user.company  # optionnel : si tu veux forcer que ça reste toujours la même company
        )

    @action(detail=True, methods=['post'])
    def find_matching_candidates(self, request, pk=None):
        """Find best candidates for this job offer"""
        job_offer = self.get_object()

        try:
            max_results = int(request.data.get('max_results', 10))
            min_score = float(request.data.get('min_score', 0))

            matching_service = MatchingService()

            job_data = {
                'id': job_offer.id,
                'title': job_offer.title,
                'requirements': job_offer.requirements or '',
                'description': job_offer.description or '',
                'experience_level': job_offer.experience_level or '',
                'location': job_offer.location or '',
                'remote_allowed': job_offer.remote_allowed
            }

            candidates = Candidate.objects.all()
            matches = []

            for candidate in candidates:
                # Check if already applied
                already_applied = Application.objects.filter(
                    candidate=candidate,
                    job_offer=job_offer
                ).exists()

                candidate_data = {
                    'id': candidate.id,
                    'skills_extracted': candidate.skills_extracted,
                    'experience_years': candidate.experience_years or 0,
                    'education_level': candidate.education_level or '',
                    'city': candidate.city or '',
                    'ai_summary': candidate.ai_summary or ''
                }

                match_result = matching_service.match_candidate_to_job(candidate_data, job_data)
                score_percentage = match_result.overall_score * 100

                # Filter by minimum score
                if score_percentage >= min_score:
                    matches.append({
                        'candidate_id': candidate.id,
                        'candidate_name': f"{candidate.first_name} {candidate.last_name}",
                        'email': candidate.email,
                        'phone': candidate.phone,
                        'city': candidate.city,
                        'experience_years': candidate.experience_years,
                        'linkedin_url': candidate.linkedin_url,
                        'skills_display': candidate.skills_extracted.get('technical_skills', [])[:5] if isinstance(
                            candidate.skills_extracted, dict) else [],
                        'overall_score': round(score_percentage, 1),
                        'recommendation': match_result.recommendation,
                        'already_applied': already_applied,
                        'breakdown': {
                            fm.field_name: {
                                'score': round(fm.similarity_score * 100, 1),
                                'confidence': fm.confidence
                            } for fm in match_result.field_matches
                        }
                    })

            # Sort by score
            matches.sort(key=lambda x: x['overall_score'], reverse=True)

            return Response({
                'success': True,
                'job_title': job_offer.title,
                'matches': matches[:max_results],
                'total_analyzed': len(candidates),
                'filters_applied': {
                    'min_score': min_score,
                    'max_results': max_results
                }
            })

        except Exception as e:
            logger.error(f"Error matching candidates for job {pk}: {e}")
            return Response({
                'success': False,
                'error': 'Error during candidate matching'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def auto_invite_best_candidates(self, request, pk=None):
        """Automatically invite best candidates"""
        job_offer = self.get_object()

        try:
            auto_invite_threshold = float(request.data.get('threshold', 80))
            max_invites = int(request.data.get('max_invites', 5))

            # Use matching to find the best
            matching_response = self.find_matching_candidates(request, pk)
            if not matching_response.data.get('success'):
                return matching_response

            best_matches = matching_response.data['matches']
            invited_candidates = []

            for match in best_matches[:max_invites]:
                if match['overall_score'] >= auto_invite_threshold and not match['already_applied']:
                    try:
                        candidate = Candidate.objects.get(id=match['candidate_id'])

                        # Create automatic application
                        application = Application.objects.create(
                            job_offer=job_offer,
                            candidate=candidate,
                            status='screening',
                            ai_match_score=int(match['overall_score']),
                            ai_analysis={
                                'auto_invited': True,
                                'matching_breakdown': match['breakdown'],
                                'invitation_date': datetime.now().isoformat()
                            },
                            source='Auto-Invitation AI'
                        )

                        invited_candidates.append({
                            'candidate_id': candidate.id,
                            'candidate_name': match['candidate_name'],
                            'score': match['overall_score'],
                            'application_id': application.id
                        })

                        # TODO: Send invitation email

                    except Exception as e:
                        logger.error(f"Error inviting candidate {match['candidate_id']}: {e}")
                        continue

            return Response({
                'success': True,
                'message': f'{len(invited_candidates)} candidates automatically invited',
                'invited_candidates': invited_candidates,
                'threshold_used': auto_invite_threshold
            })

        except Exception as e:
            logger.error(f"Auto-invitation error: {e}")
            return Response({
                'success': False,
                'error': 'Error during automatic invitation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# ================================
# NEW MATCHING ENDPOINTS
# ================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def advanced_candidate_search(request):
    """Advanced candidate search with matching"""
    try:
        search_params = {
            'skills': request.data.get('skills', []),
            'experience_min': request.data.get('experience_min', 0),
            'experience_max': request.data.get('experience_max', 20),
            'cities': request.data.get('cities', []),
            'education_levels': request.data.get('education_levels', []),
            'keyword': request.data.get('keyword', ''),
            'job_id': request.data.get('job_id', None)
        }

        # Build query
        queryset = Candidate.objects.all()

        # Apply filters
        if search_params['skills']:
            queryset = queryset.filter(
                skills_extracted__technical_skills__overlap=search_params['skills']
            )

        if search_params['experience_min'] or search_params['experience_max']:
            queryset = queryset.filter(
                experience_years__gte=search_params['experience_min'],
                experience_years__lte=search_params['experience_max']
            )

        if search_params['cities']:
            queryset = queryset.filter(city__in=search_params['cities'])

        if search_params['keyword']:
            queryset = queryset.filter(
                Q(first_name__icontains=search_params['keyword']) |
                Q(last_name__icontains=search_params['keyword']) |
                Q(cv_text__icontains=search_params['keyword']) |
                Q(ai_summary__icontains=search_params['keyword'])
            )

        candidates = list(queryset[:50])  # Limit for performance

        # Calculate matching if job_id provided
        if search_params['job_id']:
            try:
                job_offer = JobOffer.objects.get(id=search_params['job_id'])
                matching_service = MatchingService()

                enhanced_candidates = []
                for candidate in candidates:
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

                    enhanced_candidates.append({
                        'id': candidate.id,
                        'first_name': candidate.first_name,
                        'last_name': candidate.last_name,
                        'email': candidate.email,
                        'city': candidate.city,
                        'experience_years': candidate.experience_years,
                        'education_level': candidate.education_level,
                        'skills_display': candidate.skills_extracted.get('technical_skills', [])[:5] if isinstance(
                            candidate.skills_extracted, dict) else [],
                        'matching_score': round(match_result.overall_score * 100, 1),
                        'recommendation': match_result.recommendation,
                        'breakdown': {
                            fm.field_name: {
                                'score': round(fm.similarity_score * 100, 1),
                                'confidence': fm.confidence
                            } for fm in match_result.field_matches
                        }
                    })

                # Sort by score
                enhanced_candidates.sort(key=lambda x: x['matching_score'], reverse=True)

                return Response({
                    'success': True,
                    'candidates': enhanced_candidates,
                    'job_context': {
                        'id': job_offer.id,
                        'title': job_offer.title,
                        'company': job_offer.company.name if job_offer.company else 'N/A'
                    },
                    'search_params': search_params
                })

            except JobOffer.DoesNotExist:
                logger.warning(f"Job {search_params['job_id']} not found")

        # Return without matching
        candidates_data = []
        for candidate in candidates:
            candidates_data.append({
                'id': candidate.id,
                'first_name': candidate.first_name,
                'last_name': candidate.last_name,
                'email': candidate.email,
                'city': candidate.city,
                'experience_years': candidate.experience_years,
                'education_level': candidate.education_level,
                'skills_display': candidate.skills_extracted.get('technical_skills', [])[:5] if isinstance(
                    candidate.skills_extracted, dict) else []
            })

        return Response({
            'success': True,
            'candidates': candidates_data,
            'search_params': search_params
        })

    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return Response({
            'success': False,
            'error': 'Error during search'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_filters_data(request):
    """Return data for search filters"""
    try:
        # Get unique values for filters
        cities = Candidate.objects.exclude(city__isnull=True).exclude(city__exact='').values_list('city',
                                                                                                  flat=True).distinct()
        education_levels = Candidate.objects.exclude(education_level__isnull=True).exclude(
            education_level__exact='').values_list('education_level', flat=True).distinct()

        # Most common skills
        all_skills = []
        for candidate in Candidate.objects.exclude(skills_extracted__isnull=True):
            if isinstance(candidate.skills_extracted, dict):
                technical_skills = candidate.skills_extracted.get('technical_skills', [])
                if isinstance(technical_skills, list):
                    all_skills.extend(technical_skills)

        skill_counts = Counter(all_skills)
        top_skills = [skill for skill, count in skill_counts.most_common(20)]

        # Active job offers for contextual matching
        active_jobs = JobOffer.objects.filter(status='active').select_related('company').values(
            'id', 'title', 'company__name'
        )

        return Response({
            'success': True,
            'filters': {
                'cities': sorted(list(set(cities))),
                'education_levels': sorted(list(set(education_levels))),
                'top_skills': top_skills,
                'experience_range': {
                    'min': 0,
                    'max': Candidate.objects.exclude(experience_years__isnull=True).order_by(
                        '-experience_years').first().experience_years or 20
                },
                'active_jobs': list(active_jobs)
            }
        })

    except Exception as e:
        logger.error(f"Filter data error: {e}")
        return Response({
            'success': False,
            'error': 'Error loading filter data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_match_candidate_job(request):
    """Quick matching between a candidate and job offer"""
    try:
        candidate_id = request.data.get('candidate_id')
        job_id = request.data.get('job_id')

        if not candidate_id or not job_id:
            return Response({
                'success': False,
                'error': 'Candidate ID and job ID required'
            }, status=status.HTTP_400_BAD_REQUEST)

        candidate = get_object_or_404(Candidate, id=candidate_id)
        job_offer = get_object_or_404(JobOffer, id=job_id)

        # Cache check
        cache_key = f"quick_match_{candidate_id}_{job_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)

        matching_service = MatchingService()

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

        result = {
            'success': True,
            'candidate': {
                'id': candidate.id,
                'name': f"{candidate.first_name} {candidate.last_name}",
                'email': candidate.email
            },
            'job': {
                'id': job_offer.id,
                'title': job_offer.title,
                'company': job_offer.company.name if job_offer.company else 'N/A'
            },
            'matching': {
                'overall_score': round(match_result.overall_score * 100, 1),
                'recommendation': match_result.recommendation,
                'breakdown': {
                    fm.field_name: {
                        'score': round(fm.similarity_score * 100, 1),
                        'confidence': fm.confidence,
                        'candidate_value': str(fm.candidate_value)[:100],
                        'job_value': str(fm.job_value)[:100]
                    } for fm in match_result.field_matches
                }
            }
        }

        # Cache for 30 minutes
        cache.set(cache_key, result, 1800)

        return Response(result)

    except Exception as e:
        logger.error(f"Quick match error: {e}")
        return Response