# ai_engine/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ai_engine import views

app_name = 'ai_engine'
router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    # Matching candidat -> jobs


    # Test et debug



]