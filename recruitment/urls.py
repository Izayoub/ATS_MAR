# recruitment/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobOfferViewSet, CandidateViewSet, ApplicationViewSet, InterviewViewSet

router = DefaultRouter()
router.register(r'jobs', JobOfferViewSet)
router.register(r'candidates', CandidateViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'interviews', InterviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]