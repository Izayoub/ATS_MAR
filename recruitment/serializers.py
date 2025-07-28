# recruitment/serializers.py
from rest_framework import serializers
from .models import JobOffer, Candidate, Application, Interview
from accounts.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'website', 'logo', 'city']


class JobOfferSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = JobOffer
        fields = [
            'id', 'title', 'description', 'requirements', 'benefits',
            'status', 'experience_level', 'salary_min', 'salary_max',
            'location', 'remote_allowed', 'contract_type', 'company',
            'created_at', 'deadline', 'applications_count'
        ]

    def get_applications_count(self, obj):
        return obj.application_set.count()


class CandidateSerializer(serializers.ModelSerializer):
    skills_display = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'city', 'linkedin_url', 'cv_file', 'skills_extracted',
            'experience_years', 'education_level', 'ai_summary',
            'skills_display', 'created_at'
        ]

    def get_skills_display(self, obj):
        skills = obj.skills_extracted
        if isinstance(skills, dict):
            return skills.get('technical_skills', [])[:5]  # Top 5 skills
        return []


class ApplicationSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer(read_only=True)
    job_offer = JobOfferSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job_offer', 'candidate', 'status', 'status_display',
            'cover_letter', 'ai_match_score', 'cultural_fit_score',
            'applied_at', 'last_updated', 'source'
        ]


class InterviewSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)
    interviewer_name = serializers.CharField(source='interviewer.get_full_name', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'interview_type', 'scheduled_at',
            'duration_minutes', 'interviewer_name', 'questions',
            'notes', 'ai_evaluation', 'completed_at'
        ]