# ai_engine/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIProcessingViewSet

router = DefaultRouter()
router.register(r'processing', AIProcessingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]