from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from ATS_MA import settings

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
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('reviewed', 'Examiné'),
        ('interviewed', 'Entretien'),
        ('hired', 'Embauché'),
        ('rejected', 'Rejeté'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        blank=True
    )

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

    global_match_score = models.FloatField(null=True, blank=True)
    last_matching_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def current_position(self):
        """Extraire le poste actuel depuis cv_parsed_data"""
        if self.cv_parsed_data and 'professional_info' in self.cv_parsed_data:
            return self.cv_parsed_data['professional_info'].get('current_position', 'Candidat')
        return 'Candidat'


class CandidateNote(models.Model):
    NOTE_TYPES = [
        ('note', 'Note'),
        ('interview', 'Entretien'),
        ('call', 'Appel'),
        ('email', 'Email'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='note')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ corrigé
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note pour {self.candidate.full_name} - {self.created_at.date()}"
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


class MatchingProfile(models.Model):
    """Profil de préférences pour le matching"""
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='matching_profile')

    # Préférences de poste
    preferred_locations = models.JSONField(default=list)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_contract_types = models.JSONField(default=list)  # ['CDI', 'CDD', 'Freelance']
    remote_preference = models.CharField(
        max_length=20,
        choices=[
            ('required', 'Télétravail obligatoire'),
            ('preferred', 'Télétravail préféré'),
            ('accepted', 'Télétravail accepté'),
            ('refused', 'Présentiel uniquement')
        ],
        default='accepted'
    )

    # Métadonnées de matching
    last_matching_update = models.DateTimeField(auto_now=True)
    matching_active = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immédiat'),
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire')
        ],
        default='weekly'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MatchingCache(models.Model):
    """Cache des résultats de matching pour optimisation"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)

    overall_score = models.FloatField()
    detailed_scores = models.JSONField(default=dict)
    recommendation = models.CharField(max_length=20)

    # Métadonnées
    calculated_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)  # Invalider si candidat/job mis à jour

    class Meta:
        unique_together = ['candidate', 'job_offer']
        indexes = [
            models.Index(fields=['overall_score']),
            models.Index(fields=['calculated_at']),
        ]