from django.db import models


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
