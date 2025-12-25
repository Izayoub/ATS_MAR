# recruitment/urls.py - Architecture Unifiée
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    JobOfferViewSet, CandidateViewSet, ApplicationViewSet, InterviewViewSet,
    MatchingAnalyticsViewSet,GroupCandidateViewSet
)

router = DefaultRouter()
router.register(r'jobs', JobOfferViewSet, basename='joboffer')
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'interviews', InterviewViewSet, basename='interview')
router.register(r'matching', MatchingAnalyticsViewSet, basename='matching')

router.register(r'candidate-groups', GroupCandidateViewSet, basename='groupcandidate')

urlpatterns = [
    # ================================
    # API REST - Point d'entrée unique
    # ================================
    path('', include(router.urls)),

    # ================================
    # Endpoints de Matching Consolidés
    # ================================

    # Matching principal - UN SEUL endpoint par action
    path('matching/candidate-to-jobs/<int:candidate_id>/',
         views.find_jobs_for_candidate, name='find-jobs-for-candidate'),

    path('matching/job-to-candidates/<int:job_id>/',
         views.find_candidates_for_job, name='find-candidates-for-job'),

    path('matching/quick/',
         views.quick_match, name='quick-match'),

    path('matching/batch/',
         views.batch_matching, name='batch-matching'),

    # Analytics et gestion du cache
    path('matching/analytics/',
         views.matching_analytics, name='matching-analytics'),

    path('matching/cache/clear/',
         views.clear_cache, name='clear-matching-cache'),

    # ================================
    # Endpoints Utilitaires
    # ================================
    path('search/filters/',
         views.get_search_filters, name='search-filters'),

    # ================================
    # Group Candidate
    # ================================
    # Gestion des groupes de candidats
    path('groups/manage-membership/',
         views.manage_candidat_groupes, name='manage-candidat-groupes'),

    path('groups/dashboard/',
         views.groupes_dashboard, name='groupes-dashboard'),

    path('groups/suggest-for-candidat/<int:candidat_id>/',
         views.suggest_groupes_for_candidat, name='suggest-groupes-for-candidat'),

    path('upload-cv/',
         views.CandidateViewSet.as_view({'post': 'upload_cv'}),
         name='upload-cv'),

    path('pending-extraction/',
         views.CandidateViewSet.as_view({'get': 'pending_extraction'}),
         name='pending-extraction'),

    path('bulk-upload/',
         views.CandidateViewSet.as_view({'post': 'bulk_upload'}),
         name='bulk-upload'),

    path('candidates/<int:pk>/extract/',
         views.CandidateViewSet.as_view({'post': 'extract_cv_data'}),
         name='extract-cv-data'),

    # ================================
    # Vues HTML (optionnelles pour admin)
    # ================================
    path('admin/jobs/', views.admin_jobs_list, name='admin-jobs'),
    path('admin/candidates/', views.admin_candidates_list, name='admin-candidates'),
]