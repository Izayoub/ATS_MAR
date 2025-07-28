
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'company_name', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}


class CompanySerializer(serializers.ModelSerializer):
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'website', 'logo', 'address', 'city', 'phone', 'email', 'users_count']

    def get_users_count(self, obj):
        return obj.customuser_set.count()