from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Company

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'website', 'logo', 'city']


class UserRegistrationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True, max_length=200)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    accept_terms = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'role',
            'company_name', 'password', 'confirm_password', 'accept_terms'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'role': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": ["Les mots de passe ne correspondent pas"]
            })

        if not data.get('accept_terms'):
            raise serializers.ValidationError({
                "accept_terms": ["Vous devez accepter les conditions d'utilisation"]
            })

        return data

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        validated_data.pop('accept_terms')

        # Create or get company
        company, created = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'description': f"Entreprise {company_name}",
                'email': validated_data.get('email', ''),
                'city': ''
            }
        )

        # Create user
        user = User.objects.create_user(
            username=validated_data['email'],  # Use email as username
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            company=company
        )
        user.set_password(password)
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'company', 'phone', 'avatar', 'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'read_only': True},
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()