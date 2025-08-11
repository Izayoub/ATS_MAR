from django.db import models
from django.contrib.auth.models import User
import json


class AIModel(models.Model):
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50)  # mistral, bge, paddleocr, etc.
    version = models.CharField(max_length=20)
    path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProcessingJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]

    job_type = models.CharField(max_length=50)  # cv_parsing, matching, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    input_data = models.JSONField()
    output_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class MatchingLog(models.Model):
    """Log des opérations de matching pour audit"""

    cv_id = models.CharField(max_length=100)
    job_id = models.CharField(max_length=100, null=True, blank=True)
    score = models.IntegerField()
    cv_domain = models.CharField(max_length=20)
    confidence = models.FloatField()
    execution_time_ms = models.FloatField()
    from_cache = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Stockage JSON des détails
    result_details = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cv_id', 'created_at']),
            models.Index(fields=['score']),
            models.Index(fields=['cv_domain']),
        ]

    def __str__(self):
        return f"Matching {self.cv_id}: {self.score}/100 ({self.cv_domain})"


class BatchMatchingLog(models.Model):
    """Log des traitements par lot"""

    job_title = models.CharField(max_length=200)
    total_cvs = models.IntegerField()
    qualified_cvs = models.IntegerField()
    avg_score = models.FloatField()
    processing_time_ms = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Configuration utilisée
    config_used = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch {self.job_title}: {self.qualified_cvs}/{self.total_cvs} CVs"
