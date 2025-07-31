from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .models import Company
from .serializers import UserSerializer, CompanySerializer, UserRegistrationSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "description": "Registration endpoint",
            "required_fields": {
                "first_name": "string",
                "last_name": "string",
                "email": "string (will be used as username)",
                "role": "string (admin/hr_manager/recruiter/hiring_manager)",
                "company_name": "string",
                "password": "string (min 8 chars)",
                "confirm_password": "string",
                "accept_terms": "boolean (must be true)"
            }
        })

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "Compte créé avec succès!",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.get_role_display(),
                    "company": user.company.name if user.company else None
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)