
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .models import Company, CustomUser
from .serializers import UserSerializer, CompanySerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            company_name = request.data.get('company_name')

            # Créer la company
            company = Company.objects.create(
                name=company_name,
                description=request.data.get('company_description', '')
            )

            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                company=company,
                role='admin'
            )

            # Générer token
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'success': True,
                'token': token.key,
                'user': UserSerializer(user).data
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company)


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company.id)
