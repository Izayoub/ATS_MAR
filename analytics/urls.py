from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsViewSet, RecruitmentMetricViewSet, DashboardWidgetViewSet

router = DefaultRouter()
router.register(r'overview', AnalyticsViewSet, basename='analytics')
router.register(r'metrics', RecruitmentMetricViewSet,basename='metrics')
router.register(r'widgets', DashboardWidgetViewSet, basename='widgets')

urlpatterns = [
    path('', include(router.urls)),
]