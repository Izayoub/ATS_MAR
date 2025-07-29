# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserViewSet, CompanyViewSet, RegisterView

router = DefaultRouter()
router.register(r'users', UserViewSet , basename='user')
router.register(r'companies', CompanyViewSet,basename='company')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('register/', RegisterView.as_view(), name='register'),
]