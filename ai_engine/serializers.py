# ai_engine/serializers.py
from rest_framework import serializers
from .models import ProcessingJob, AIModel


class ProcessingJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingJob
        fields = ['id', 'job_type', 'status', 'input_data', 'output_data', 'error_message', 'created_at',
                  'completed_at']


class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ['id', 'name', 'model_type', 'version', 'is_active', 'created_at']

class CVDataSerializer(serializers.Serializer):
    titre_candidat = serializers.CharField(max_length=200)
    profil_resume = serializers.CharField()
    formations = serializers.ListField(child=serializers.CharField(), default=list)
    experience_years = serializers.IntegerField(min_value=0, default=0)
    competences_techniques = serializers.ListField(child=serializers.CharField(), default=list)
    competences_informatiques = serializers.ListField(child=serializers.CharField(), default=list)
    langues = serializers.ListField(child=serializers.CharField(), default=list)
    certifications = serializers.ListField(child=serializers.CharField(), default=list)
    projets = serializers.ListField(child=serializers.CharField(), default=list)
    soft_skills = serializers.ListField(child=serializers.CharField(), default=list)

class JobExigencesSerializer(serializers.Serializer):
    formation_requise = serializers.CharField(default="")
    annees_experience = serializers.IntegerField(min_value=0, default=0)
    competences_obligatoires = serializers.ListField(child=serializers.CharField(), default=list)
    competences_souhaitees = serializers.ListField(child=serializers.CharField(), default=list)
    langues = serializers.ListField(child=serializers.CharField(), default=list)
    certifications = serializers.ListField(child=serializers.CharField(), default=list)
    outils = serializers.ListField(child=serializers.CharField(), default=list)
    qualites_humaines = serializers.ListField(child=serializers.CharField(), default=list)

class JobDataSerializer(serializers.Serializer):
    titre_poste = serializers.CharField(max_length=200)
    missions = serializers.CharField()
    exigences = JobExigencesSerializer(default=dict)

class MatchingRequestSerializer(serializers.Serializer):
    cv_data = CVDataSerializer()
    job_data = JobDataSerializer()
    cv_id = serializers.CharField(required=False)
    use_cache = serializers.BooleanField(default=True)

class BatchMatchingRequestSerializer(serializers.Serializer):
    cv_list = serializers.ListField(child=CVDataSerializer())
    job_data = JobDataSerializer()
    top_k = serializers.IntegerField(default=10, min_value=1, max_value=100)
    prioritize_tech = serializers.BooleanField(default=True)
