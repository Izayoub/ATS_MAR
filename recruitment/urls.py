# recruitment/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

#from . import views, views_cv_integration
from .views import JobOfferViewSet, CandidateViewSet, ApplicationViewSet, InterviewViewSet, advanced_candidate_search, \
    real_time_matching_stats, debug_matching
from . import views
router = DefaultRouter()
router.register(r'jobs', JobOfferViewSet,basename='joboffer')
router.register(r'candidates', CandidateViewSet,basename='candidate')
router.register(r'applications', ApplicationViewSet,basename='application')
router.register(r'interviews', InterviewViewSet,basename='interview')

#cv_integration_patterns = [
    # Upload et parsing de CV
# path('cv/upload/', views_cv_integration.cv_upload_and_parse, name='cv_upload_and_parse'),
    #path('cv/text-parse/', views_cv_integration.cv_text_parse_ajax, name='cv_text_parse_ajax'),

    # Traitement en lot
    #path('cv/batch-upload/', views_cv_integration.cv_batch_upload, name='cv_batch_upload'),
    #path('cv/batch-results/', views_cv_integration.cv_batch_results, name='cv_batch_results'),

    # Mise à jour candidat
# path('candidate/<int:pk>/update-cv/', views_cv_integration.candidate_update_from_cv,
# name='candidate_update_from_cv'),
    #path('candidate/<int:pk>/parsed-data/', views_cv_integration.candidate_parsed_data_view,
         #name='candidate_parsed_data_view'),

    # Statistiques
# path('cv/stats/', views_cv_integration.cv_parsing_stats, name='cv_parsing_stats'),
#]

urlpatterns = [
    path('', include(router.urls)),

    # HTML Views
path('candidates/<int:pk>/notes/', CandidateViewSet.as_view({'get': 'notes', 'post': 'notes'}), name='candidate-notes'),
    path('candidates/<int:pk>/timeline/', CandidateViewSet.as_view({'get': 'timeline'}), name='candidate-timeline'),
    path('candidates/<int:pk>/status/', CandidateViewSet.as_view({'patch': 'update_status'}), name='candidate-status'),
    path('candidates/search/advanced/', advanced_candidate_search, name='advanced_candidate_search'),
    path('candidates/filters-data/', views.get_search_filters_data, name='get_search_filters_data'),
    path('matching/stats/', real_time_matching_stats, name='real_time_matching_stats'),
    path('matching/debug/', debug_matching, name='debug_matching'),
    #path('jobs/', views.joboffer_list, name='joboffer_list'),
    #path('jobs/<int:pk>/', views.joboffer_detail, name='joboffer_detail'),
    #path('jobs/create/', views.joboffer_create, name='joboffer_create'),
    #path('jobs/<int:pk>/edit/', views.joboffer_update, name='joboffer_update'),
    #path('jobs/<int:pk>/delete/', views.joboffer_delete, name='joboffer_delete'),
    path('jobs', JobOfferViewSet.as_view({'get': 'list'}), name='jobs'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/edit/', views.company_update, name='company_update'),

]#+ cv_integration_patterns

