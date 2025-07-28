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