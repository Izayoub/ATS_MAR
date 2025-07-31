from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'email', 'website']

class UserRegistrationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True)
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
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Les mots de passe ne correspondent pas"}
            )
        if not data['accept_terms']:
            raise serializers.ValidationError(
                {"accept_terms": "Vous devez accepter les conditions"}
            )
        return data

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        validated_data.pop('accept_terms')

        company, _ = Company.objects.get_or_create(
            name=company_name,
            defaults={'email': validated_data['email']}
        )

        user = User.objects.create_user(
            username=validated_data['email'],
            company=company,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'company', 'phone', 'avatar'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'read_only': True},
        }