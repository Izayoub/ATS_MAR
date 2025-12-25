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

    # Nouveaux champs pour le matching personnalisé
    matching_weights = models.JSONField(
        default=dict,
        blank=True,
        help_text="Poids personnalisés pour le matching (ex: {'technical_skills': 0.4, 'experience': 0.3, ...})"
    )
    system_prompt = models.TextField(
        blank=True,
        help_text="Prompt système spécifique pour ce job, utilisé par le modèle IA"
    )

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    def get_matching_weights(self):
        """Retourne les poids de matching, avec fallback sur les valeurs par défaut"""
        default_weights = {
            'technical_skills': 0.35,
            'soft_skills': 0.15,
            'experience': 0.30,
            'education': 0.20
        }

        if not self.matching_weights:
            return default_weights

        # Merger avec les valeurs par défaut pour s'assurer que tous les champs sont présents
        weights = default_weights.copy()
        weights.update(self.matching_weights)

        # Normaliser les poids pour qu'ils somment à 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        return weights

    def get_system_prompt(self):
        """Retourne le prompt système ou un prompt par défaut"""
        if self.system_prompt:
            return self.system_prompt

        return f"""Vous êtes un expert en recrutement analysant des candidats pour le poste de "{self.title}". 
        Évaluez la compatibilité en vous concentrant sur les compétences techniques, l'expérience, 
        et l'adéquation culturelle avec l'entreprise {self.company.name if self.company else "l'entreprise"}.

        Critères d'évaluation:
        - Niveau d'expérience: {self.get_experience_level_display()}
        - Type de contrat: {self.contract_type}
        - Télétravail autorisé: {'Oui' if self.remote_allowed else 'Non'}

        Soyez précis et objectif dans votre analyse. """

    def has_custom_matching_config(self):
        """Check if this job has custom matching configuration"""
        return bool(self.matching_weights or self.system_prompt)

    def reset_matching_config(self):
        """Reset matching configuration to defaults"""
        self.matching_weights = {}
        self.system_prompt = ''
        self.save(update_fields=['matching_weights', 'system_prompt'])

class Candidate(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('N/A', 'Non spécifié'),  # Ajout option N/A
    ]
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('pending_extraction', 'En attente d\'extraction'),  # Nouveau statut
        ('reviewed', 'Examiné'),
        ('interviewed', 'Entretien'),
        ('hired', 'Embauché'),
        ('rejected', 'Rejeté'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_extraction',  # Nouveau défaut
        blank=True
    )

    # Champs obligatoires minimums
    first_name = models.CharField(max_length=100, default='N/A')
    last_name = models.CharField(max_length=100, default='N/A')
    email = models.EmailField(unique=True, null=True, blank=True)  # Maintenant optionnel

    # Tous les autres champs deviennent optionnels avec N/A par défaut
    phone = models.CharField(max_length=20, blank=True, default='N/A')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='N/A')
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, default='N/A')
    city = models.CharField(max_length=100, blank=True, default='N/A')
    linkedin_url = models.URLField(blank=True, default='')

    # CV et parsing
    cv_file = models.FileField(upload_to='cvs/', null=True, blank=True)
    cv_file_path = models.CharField(max_length=500, blank=True)  # NOUVEAU CHAMP
    cv_text = models.TextField(blank=True)
    cv_parsed_data = models.JSONField(default=dict)

    # Compétences avec valeurs par défaut
    technical_skills = models.JSONField(default=list)
    soft_skills = models.JSONField(default=list)
    skills_extracted = models.JSONField(default=dict, blank=True)

    # Autres champs optionnels
    experience_years = models.IntegerField(null=True, blank=True)
    education_level = models.CharField(max_length=100, blank=True, default='N/A')
    languages = models.JSONField(default=list)
    ai_summary = models.TextField(blank=True, default='')

    # Champs de matching
    global_match_score = models.FloatField(null=True, blank=True)
    last_matching_date = models.DateTimeField(null=True, blank=True)

    # Nouveau champ pour tracking extraction
    is_extracted = models.BooleanField(default=False)
    extraction_date = models.DateTimeField(null=True, blank=True)

    # === NOUVEAUX CHAMPS EMBEDDINGS ===
    cv_embeddings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Embeddings structurés',
        help_text='Embeddings vectoriels organisés par section du CV en format JSON structuré'
    )

    embeddings_generated_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Embeddings générés le',
        help_text='Date et heure de génération des embeddings'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        if self.first_name == 'N/A' and self.last_name == 'N/A':
            return f"Candidat #{self.id}"
        return f"{self.first_name} {self.last_name}"

    def mark_as_extracted(self):
        """Marquer le candidat comme extrait"""
        self.is_extracted = True
        self.extraction_date = timezone.now()
        self.status = 'new'  # Passer au statut normal après extraction
        self.save()

    def has_embeddings(self):
        """Vérifier si le candidat a des embeddings générés"""
        return bool(self.cv_embeddings and self.embeddings_generated_at)

    def mark_embeddings_generated(self):
        """Marquer la génération des embeddings"""
        self.embeddings_generated_at = timezone.now()
        self.save(update_fields=['embeddings_generated_at'])

    def get_embedding_section(self, section_name):
        """Récupérer les embeddings d'une section spécifique"""
        return self.cv_embeddings.get(section_name, [])

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"



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

    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE,related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,related_name='applications')
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


class GroupCandidate(models.Model):
    """Groupe pour catégoriser les candidats"""

    TYPE_CHOICES = [
        ('competence', 'Par compétence'),
        ('experience', 'Par expérience'),
        ('projet', 'Par projet'),
        ('pipeline', 'Pipeline de recrutement'),
        ('performance', 'Par performance'),
        ('geographic', 'Par zone géographique'),
        ('custom', 'Personnalisé'),
    ]

    COLOR_CHOICES = [
        ('blue', 'Bleu'),
        ('green', 'Vert'),
        ('red', 'Rouge'),
        ('yellow', 'Jaune'),
        ('purple', 'Violet'),
        ('orange', 'Orange'),
        ('gray', 'Gris'),
        ('teal', 'Sarcelle'),
    ]

    # Informations de base
    nom = models.CharField(max_length=200, verbose_name="Nom du groupe")
    description = models.TextField(blank=True, verbose_name="Description")

    # Classification
    type_groupe = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='custom',
        verbose_name="Type de groupe"
    )

    # Organisation visuelle
    couleur = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default='blue',
        verbose_name="Couleur"
    )
    ordre_affichage = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    # Relations
    candidats = models.ManyToManyField(
        'Candidate',  # Use string reference to avoid import issues
        related_name='groupes',
        blank=True,
        verbose_name="Candidats"
    )

    # Propriétaire et permissions
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Créé par"
    )

    # Paramètres
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_public = models.BooleanField(
        default=False,
        verbose_name="Visible par tous les utilisateurs de l'entreprise"
    )

    # Auto-population fields
    auto_populate = models.BooleanField(
        default=False,
        verbose_name="Population automatique"
    )
    criteria_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Critères automatiques"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Groupe de candidats"
        verbose_name_plural = "Groupes de candidats"
        ordering = ['ordre_affichage', 'nom']
        constraints = [
            models.UniqueConstraint(
                fields=['nom', 'created_by'],
                name='unique_group_name_per_user'
            )
        ]

    def __str__(self):
        return f"{self.nom} ({self.get_candidats_count()} candidats)"

    def get_candidats_count(self):
        """Méthode pour obtenir le nombre de candidats - remplace la property"""
        return self.candidats.count()

    @property
    def skills_distribution(self):
        """Distribution des compétences dans le groupe"""
        technical_skills = []
        soft_skills = []

        for candidat in self.candidats.all():
            # Handle cases where skills might not exist
            tech_skills = getattr(candidat, 'technical_skills', None)
            if tech_skills and isinstance(tech_skills, list):
                technical_skills.extend(tech_skills)

            s_skills = getattr(candidat, 'soft_skills', None)
            if s_skills and isinstance(s_skills, list):
                soft_skills.extend(s_skills)

        from collections import Counter
        return {
            'technical': dict(Counter(technical_skills).most_common(10)),
            'soft': dict(Counter(soft_skills).most_common(10))
        }

    @property
    def experience_distribution(self):
        """Distribution des années d'expérience"""
        try:
            experience_data = self.candidats.exclude(
                experience_years__isnull=True
            ).values_list('experience_years', flat=True)

            if not experience_data:
                return {}

            return {
                'min': min(experience_data),
                'max': max(experience_data),
                'avg': sum(experience_data) / len(experience_data),
                'distribution': {
                    '0-2': len([x for x in experience_data if 0 <= x <= 2]),
                    '3-5': len([x for x in experience_data if 3 <= x <= 5]),
                    '6-10': len([x for x in experience_data if 6 <= x <= 10]),
                    '10+': len([x for x in experience_data if x > 10])
                }
            }
        except Exception:
            return {}

    def add_candidat(self, candidat):
        """Ajouter un candidat au groupe"""
        self.candidats.add(candidat)
        self.updated_at = timezone.now()
        self.save(update_fields=['updated_at'])

    def remove_candidat(self, candidat):
        """Retirer un candidat du groupe"""
        self.candidats.remove(candidat)
        self.updated_at = timezone.now()
        self.save(update_fields=['updated_at'])

    def apply_auto_criteria(self):
        """Appliquer les critères automatiques pour peupler le groupe"""
        if not self.auto_populate or not self.criteria_json:
            return 0

        try:
            from .models import Candidate  # Import here to avoid circular imports

            criteria = self.criteria_json
            queryset = Candidate.objects.all()

            # Filtres disponibles
            if 'technical_skills' in criteria:
                skills = criteria['technical_skills']
                if isinstance(skills, list) and skills:
                    # Check if the field exists before filtering
                    if hasattr(Candidate, 'technical_skills'):
                        queryset = queryset.filter(technical_skills__overlap=skills)

            if 'min_experience' in criteria:
                min_exp = criteria['min_experience']
                if isinstance(min_exp, int):
                    if hasattr(Candidate, 'experience_years'):
                        queryset = queryset.filter(experience_years__gte=min_exp)

            if 'max_experience' in criteria:
                max_exp = criteria['max_experience']
                if isinstance(max_exp, int):
                    if hasattr(Candidate, 'experience_years'):
                        queryset = queryset.filter(experience_years__lte=max_exp)

            if 'education_levels' in criteria:
                edu_levels = criteria['education_levels']
                if isinstance(edu_levels, list) and edu_levels:
                    if hasattr(Candidate, 'education_level'):
                        queryset = queryset.filter(education_level__in=edu_levels)

            if 'cities' in criteria:
                cities = criteria['cities']
                if isinstance(cities, list) and cities:
                    if hasattr(Candidate, 'city'):
                        queryset = queryset.filter(city__in=cities)

            if 'min_match_score' in criteria:
                min_score = criteria['min_match_score']
                if isinstance(min_score, (int, float)):
                    if hasattr(Candidate, 'global_match_score'):
                        queryset = queryset.filter(global_match_score__gte=min_score / 100)

            # Ajouter les candidats correspondants
            new_candidates = queryset.exclude(id__in=self.candidats.values_list('id', flat=True))
            added_count = 0

            for candidate in new_candidates:
                self.candidats.add(candidate)
                added_count += 1

            self.last_sync = timezone.now()
            self.save(update_fields=['last_sync'])

            return added_count
        except Exception as e:
            # Log error and return 0
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error applying auto criteria for group {self.id}: {e}")
            return 0

    def get_analytics(self):
        """Analytics complètes du groupe"""
        try:
            candidats = self.candidats.all()

            if not candidats.exists():
                return {
                    'total': 0,
                    'message': 'Aucun candidat dans ce groupe'
                }

            analytics = {
                'total': candidats.count(),
                'skills': self.skills_distribution,
                'experience': self.experience_distribution,
            }

            # Add status distribution if status field exists
            if hasattr(candidats.model, 'status'):
                analytics['status_distribution'] = dict(
                    candidats.values('status').annotate(
                        count=models.Count('id')
                    ).values_list('status', 'count')
                )

            # Add applications count if applications relation exists
            try:
                analytics['applications_count'] = sum(
                    candidat.applications.count() if hasattr(candidat, 'applications') else 0
                    for candidat in candidats
                )
            except Exception:
                analytics['applications_count'] = 0

            # Add average match score if field exists
            if hasattr(candidats.model, 'global_match_score'):
                analytics['avg_match_score'] = candidats.aggregate(
                    avg_score=models.Avg('global_match_score')
                )['avg_score']
            else:
                analytics['avg_match_score'] = None

            analytics.update({
                'last_updated': self.updated_at,
                'last_sync': self.last_sync
            })

            return analytics
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting analytics for group {self.id}: {e}")
            return {
                'total': 0,
                'error': 'Erreur lors du calcul des analytics'
            }
