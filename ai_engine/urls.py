# ai_engine/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIProcessingViewSet
from . import views

app_name = 'ai_engine'
router = DefaultRouter()
router.register(r'processing', AIProcessingViewSet,basename='processing')

urlpatterns = [
    path('', include(router.urls)),
    path('match-cv/', views.MatchingViews.match_single_cv, name='match_single_cv'),
    path('batch-match/', views.MatchingViews.batch_matching, name='batch_matching'),
    path('analyze-gaps/', views.MatchingViews.analyze_gaps, name='analyze_gaps'),
    path('health/', views.MatchingViews.health_check, name='health_check'),

    # Interface de test
    path('testeur/', views.MatchingViews.testeur_interface, name='testeur'),
]