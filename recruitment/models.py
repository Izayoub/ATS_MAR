from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class JobOffer(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('paused', 'En pause'),
        ('closed', 'Fermée'),
    ]

    EXPERIENCE_CHOICES = [
        ('junior', 'Junior (0-2 ans)'),
        ('middle', 'Confirmé (2-5 ans)'),
        ('senior', 'Senior (5+ ans)'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200)
    remote_allowed = models.BooleanField(default=False)
    contract_type = models.CharField(max_length=50, default='CDI')
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)

    # Champs IA
    ai_generated = models.BooleanField(default=False)
    seo_optimized = models.BooleanField(default=False)
    bias_checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.company.name}"


class Candidate(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)

    # CV et parsing
    cv_file = models.FileField(upload_to='cvs/', null=True, blank=True)
    cv_text = models.TextField(blank=True)  # Texte extrait par OCR
    cv_parsed_data = models.JSONField(default=dict)  # Données structurées par IA

    # Métadonnées IA
    skills_extracted = models.JSONField(default=list)
    experience_years = models.IntegerField(null=True, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    languages = models.JSONField(default=list)
    ai_summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('received', 'Reçu'),
        ('screening', 'Pré-sélection'),
        ('interview', 'Entretien'),
        ('tests', 'Test technique'),
        ('final', 'Entretien final'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
        ('withdrawn', 'Retiré'),
    ]

    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    cover_letter = models.TextField(blank=True)

    # Scoring IA
    ai_match_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    ai_analysis = models.JSONField(default=dict)
    cultural_fit_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )

    # Métadonnées
    applied_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, blank=True)  # ReKrute, LinkedIn, etc.

    class Meta:
        unique_together = ['job_offer', 'candidate']

    def __str__(self):
        return f"{self.candidate} -> {self.job_offer.title}"


class Interview(models.Model):
    TYPE_CHOICES = [
        ('phone', 'Téléphonique'),
        ('video', 'Visioconférence'),
        ('in_person', 'Présentiel'),
        ('ai_screening', 'Pré-sélection IA'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    interview_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE)

    # Contenu IA
    questions = models.JSONField(default=list)  # Questions générées par IA
    notes = models.TextField(blank=True)
    recording_file = models.FileField(upload_to='interviews/', null=True, blank=True)
    transcription = models.TextField(blank=True)
    ai_evaluation = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Entretien {self.application.candidate} - {self.scheduled_at}"