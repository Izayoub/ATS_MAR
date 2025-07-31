# recruitment/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import JobOfferViewSet, CandidateViewSet, ApplicationViewSet, InterviewViewSet

router = DefaultRouter()
router.register(r'jobs', JobOfferViewSet,basename='joboffer')
router.register(r'candidates', CandidateViewSet,basename='candidate')
router.register(r'applications', ApplicationViewSet,basename='application')
router.register(r'interviews', InterviewViewSet,basename='interview')

urlpatterns = [
    path('', include(router.urls)),

    # HTML Views
    path('joboffers/', views.joboffer_list, name='joboffer_list'),
    path('joboffers/<int:pk>/', views.joboffer_detail, name='joboffer_detail'),
    path('joboffers/create/', views.joboffer_create, name='joboffer_create'),
    path('joboffers/<int:pk>/edit/', views.joboffer_update, name='joboffer_update'),
    path('joboffers/<int:pk>/delete/', views.joboffer_delete, name='joboffer_delete'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/edit/', views.company_update, name='company_update'),
    path('companies/<int:pk>/delete/', views.company_delete, name='company_delete'),
]