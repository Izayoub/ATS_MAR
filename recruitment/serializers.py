from rest_framework import serializers

from accounts.serializers import CompanySerializer
from .models import JobOffer, Candidate, Application, Interview, CandidateNote


class CandidateMatchingSerializer(serializers.ModelSerializer):
    """Specialized serializer for matching with scores"""
    skills_display = serializers.SerializerMethodField()
    matching_score = serializers.SerializerMethodField()
    matching_breakdown = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'city', 'experience_years', 'education_level', 'linkedin_url',
            'skills_display', 'matching_score', 'matching_breakdown', 'created_at'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_skills_display(self, obj):
        skills = obj.skills_extracted
        if isinstance(skills, dict):
            return skills.get('technical_skills', [])[:5]
        return []

    def get_matching_score(self, obj):
        # Score calculated dynamically by matching service
        return getattr(obj, 'matching_score', None)

    def get_matching_breakdown(self, obj):
        # Details calculated dynamically
        return getattr(obj, 'matching_details', {})


class JobOfferMatchingSerializer(serializers.ModelSerializer):
    """Serializer for job offers with matching context"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    applications_count = serializers.SerializerMethodField()
    avg_matching_score = serializers.SerializerMethodField()
    top_candidate_score = serializers.SerializerMethodField()

    class Meta:
        model = JobOffer
        fields = [
            'id', 'title', 'description', 'requirements', 'experience_level',
            'location', 'remote_allowed', 'contract_type', 'salary_min', 'salary_max',
            'company_name', 'applications_count', 'avg_matching_score',
            'top_candidate_score', 'status', 'created_at'
        ]

    def get_applications_count(self, obj):
        return obj.application_set.count()

    def get_avg_matching_score(self, obj):
        applications = obj.application_set.exclude(ai_match_score__isnull=True)
        if applications.exists():
            return round(applications.aggregate(avg=serializers.models.Avg('ai_match_score'))['avg'], 1)
        return None

    def get_top_candidate_score(self, obj):
        top_application = obj.application_set.exclude(ai_match_score__isnull=True).order_by('-ai_match_score').first()
        return top_application.ai_match_score if top_application else None


class ApplicationEnhancedSerializer(serializers.ModelSerializer):
    """Enhanced application serializer with matching details"""
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    job_title = serializers.CharField(source='job_offer.title', read_only=True)
    company_name = serializers.CharField(source='job_offer.company.name', read_only=True)
    matching_recommendation = serializers.SerializerMethodField()
    skills_match_details = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'candidate', 'candidate_name', 'candidate_email',
            'job_offer', 'job_title', 'company_name',
            'status', 'ai_match_score', 'matching_recommendation',
            'skills_match_details', 'applied_at', 'updated_at'
        ]

    def get_matching_recommendation(self, obj):
        if obj.ai_analysis and isinstance(obj.ai_analysis, dict):
            return obj.ai_analysis.get('recommendation', 'No recommendation')
        return 'No analysis available'

    def get_skills_match_details(self, obj):
        if obj.ai_analysis and isinstance(obj.ai_analysis, dict):
            breakdown = obj.ai_analysis.get('breakdown', {})
            return {
                skill: round(score * 100, 1) if isinstance(score, (int, float)) else score
                for skill, score in breakdown.items()
            }
        return {}


class InterviewEnhancedSerializer(serializers.ModelSerializer):
    """Enhanced interview serializer with AI suggestions"""
    candidate_name = serializers.CharField(source='application.candidate.get_full_name', read_only=True)
    job_title = serializers.CharField(source='application.job_offer.title', read_only=True)
    matching_score = serializers.CharField(source='application.ai_match_score', read_only=True)
    interview_suggestions = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'candidate_name', 'job_title', 'matching_score',
            'interview_type', 'scheduled_date', 'status', 'interviewer',
            'notes', 'score', 'interview_suggestions', 'created_at'
        ]

    def get_interview_suggestions(self, obj):
        # This would be populated by the AI interview prep endpoint
        return getattr(obj, 'ai_suggestions', {})


# ================================
# Existing Serializers (Enhanced)
# ================================

class CandidateSerializer(serializers.ModelSerializer):
    skills_summary = serializers.SerializerMethodField()
    experience_summary = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = '__all__'

    def get_skills_summary(self, obj):
        """Get a readable summary of skills"""
        if isinstance(obj.skills_extracted, dict):
            technical = obj.skills_extracted.get('technical_skills', [])
            soft = obj.skills_extracted.get('soft_skills', [])
            return {
                'technical_count': len(technical) if isinstance(technical, list) else 0,
                'soft_count': len(soft) if isinstance(soft, list) else 0,
                'top_technical': technical[:5] if isinstance(technical, list) else []
            }
        return {'technical_count': 0, 'soft_count': 0, 'top_technical': []}

    def get_experience_summary(self, obj):
        """Get experience summary"""
        return {
            'years': obj.experience_years or 0,
            'level': obj.education_level or 'Not specified'
        }

    def get_application_count(self, obj):
        return obj.application_set.count()


class JobOfferSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)  # lecture seule
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = JobOffer
        fields = [
            'id', 'title', 'description', 'requirements', 'benefits',
            'status', 'experience_level', 'salary_min', 'salary_max',
            'location', 'remote_allowed', 'contract_type', 'company',
            'created_at', 'deadline', 'applications_count'
        ]
        read_only_fields = ['company', 'created_at', 'applications_count']

    def get_applications_count(self, obj):
        return obj.application_set.count()



class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job_offer.title', read_only=True)
    matching_quality = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = '__all__'

    def get_matching_quality(self, obj):
        """Categorize matching quality"""
        score = obj.ai_match_score
        if score is None:
            return 'Not analyzed'
        elif score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Poor'


class InterviewSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='application.candidate.get_full_name', read_only=True)
    job_title = serializers.CharField(source='application.job_offer.title', read_only=True)

    class Meta:
        model = Interview
        fields = '__all__'


class CandidateNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = CandidateNote
        fields = ['id', 'content', 'note_type', 'author_name', 'created_at']


class CandidateDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour la vue détail candidat"""

    full_name = serializers.CharField(read_only=True)
    current_position = serializers.CharField(read_only=True)
    skills_list = serializers.SerializerMethodField()
    languages_list = serializers.SerializerMethodField()
    certifications_list = serializers.SerializerMethodField()
    portfolio_url = serializers.SerializerMethodField()
    github_url = serializers.SerializerMethodField()
    website_url = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    notes_count = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'gender', 'birth_date', 'address', 'city', 'linkedin_url',
            'cv_file', 'cv_text', 'cv_parsed_data', 'skills_extracted',
            'experience_years', 'education_level', 'languages', 'ai_summary',
            'status', 'global_match_score', 'last_matching_date',
            'created_at', 'updated_at', 'current_position',
            'skills_list', 'languages_list', 'certifications_list',
            'portfolio_url', 'github_url', 'website_url',
            'applications_count', 'notes_count'
        ]

    def get_skills_list(self, obj):
        """Extraire les compétences depuis skills_extracted"""
        skills = obj.skills_extracted
        if isinstance(skills, dict):
            return skills.get('technical_skills', [])
        elif isinstance(skills, list):
            return skills
        return []

    def get_languages_list(self, obj):
        """Formatter les langues"""
        return obj.languages if obj.languages else []

    def get_certifications_list(self, obj):
        """Extraire les certifications depuis cv_parsed_data"""
        if obj.cv_parsed_data and 'certifications' in obj.cv_parsed_data:
            return obj.cv_parsed_data['certifications']
        return []

    def get_portfolio_url(self, obj):
        """Extraire portfolio depuis cv_parsed_data"""
        if obj.cv_parsed_data and 'contact' in obj.cv_parsed_data:
            return obj.cv_parsed_data['contact'].get('portfolio', '')
        return ''

    def get_github_url(self, obj):
        """Extraire GitHub depuis cv_parsed_data"""
        if obj.cv_parsed_data and 'contact' in obj.cv_parsed_data:
            return obj.cv_parsed_data['contact'].get('github', '')
        return ''

    def get_website_url(self, obj):
        """Extraire site web depuis cv_parsed_data"""
        if obj.cv_parsed_data and 'contact' in obj.cv_parsed_data:
            return obj.cv_parsed_data['contact'].get('website', '')
        return ''

    def get_applications_count(self, obj):
        return obj.application_set.count()

    def get_notes_count(self, obj):
        return obj.notes.count()