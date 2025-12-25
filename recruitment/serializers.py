# recruitment/serializers.py - Serializers Unifiés
from rest_framework import serializers
from django.db import models
from django.contrib.auth import get_user_model

from accounts.serializers import CompanySerializer
from .models import JobOffer, Candidate, Application, Interview, CandidateNote, MatchingCache,GroupCandidate

User = get_user_model()


class BaseCandidateSerializer(serializers.ModelSerializer):
    """Serializer de base pour Candidate - à hériter selon le contexte"""
    full_name = serializers.ReadOnlyField()
    current_position = serializers.ReadOnlyField()
    has_embeddings = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'gender', 'birth_date', 'address', 'city', 'linkedin_url',
            'technical_skills', 'soft_skills', 'experience_years',
            'education_level', 'languages', 'status', 'current_position',
            'has_embeddings', 'created_at', 'updated_at'
        ]

    def get_has_embeddings(self, obj):
        return obj.has_embeddings()

class CandidateListSerializer(BaseCandidateSerializer):
    """Pour la liste des candidats - données essentielles"""
    skills_summary = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()

    class Meta(BaseCandidateSerializer.Meta):
        fields = BaseCandidateSerializer.Meta.fields + [
            'skills_summary', 'application_count', 'global_match_score'
        ]

    def get_skills_summary(self, obj):
        tech_count = len(obj.technical_skills or [])
        soft_count = len(obj.soft_skills or [])
        return {
            'technical_count': tech_count,
            'soft_count': soft_count,
            'top_technical': (obj.technical_skills or [])[:3]
        }

    def get_application_count(self, obj):
        return getattr(obj, 'applications_count', 0)


class CandidateDetailSerializer(BaseCandidateSerializer):
    """Pour le détail d'un candidat - toutes les données"""
    cv_text = serializers.CharField(read_only=True)
    cv_parsed_data = serializers.JSONField(read_only=True)
    ai_summary = serializers.CharField(read_only=True)
    skills_breakdown = serializers.SerializerMethodField()
    recent_applications = serializers.SerializerMethodField()
    matching_stats = serializers.SerializerMethodField()
    embeddings_info = serializers.SerializerMethodField()

    class Meta(BaseCandidateSerializer.Meta):
        fields = BaseCandidateSerializer.Meta.fields + [
            'cv_file', 'cv_text', 'cv_parsed_data', 'ai_summary',
            'skills_breakdown', 'recent_applications', 'matching_stats',
            'global_match_score', 'last_matching_date', 'embeddings_info',
            'embeddings_generated_at'
        ]

    def get_skills_breakdown(self, obj):
        return {
            'technical': {
                'count': len(obj.technical_skills or []),
                'skills': obj.technical_skills or []
            },
            'soft': {
                'count': len(obj.soft_skills or []),
                'skills': obj.soft_skills or []
            },
            'languages': obj.languages or []
        }

    def get_recent_applications(self, obj):
        recent = getattr(obj, 'recent_applications_prefetch',
                         obj.applications.select_related('job_offer', 'job_offer__company')[:5])

        return [{
            'id': app.id,
            'job_title': app.job_offer.title,
            'company': app.job_offer.company.name if app.job_offer.company else 'N/A',
            'status': app.status,
            'applied_at': app.applied_at,
            'match_score': app.ai_match_score
        } for app in recent]

    def get_matching_stats(self, obj):
        # Stats depuis le cache de matching
        cache_stats = MatchingCache.objects.filter(
            candidate=obj, is_valid=True
        ).aggregate(
            count=models.Count('id'),
            avg_score=models.Avg('overall_score'),
            excellent_count=models.Count('id', filter=models.Q(overall_score__gte=0.8)),
            good_count=models.Count('id', filter=models.Q(overall_score__gte=0.6, overall_score__lt=0.8))
        )

        return {
            'total_matches': cache_stats['count'] or 0,
            'average_score': round((cache_stats['avg_score'] or 0) * 100, 1),
            'excellent_matches': cache_stats['excellent_count'] or 0,
            'good_matches': cache_stats['good_count'] or 0,
            'last_updated': obj.last_matching_date
        }

    def get_embeddings_info(self, obj):
        """Information sur les embeddings du candidat"""
        if not obj.has_embeddings():
            return {
                'available': False,
                'generated_at': None,
                'sections': []
            }

        sections = list(obj.cv_embeddings.keys()) if obj.cv_embeddings else []
        return {
            'available': True,
            'generated_at': obj.embeddings_generated_at,
            'sections': sections,
            'total_sections': len(sections)
        }

    def get_groupes_info(self, obj):
        """Information sur les groupes du candidat"""
        groupes = obj.groupes.all()
        return [{
            'id': groupe.id,
            'nom': groupe.nom,
            'couleur': groupe.couleur,
            'type_groupe': groupe.type_groupe
        } for groupe in groupes]


class CandidateUploadSerializer(serializers.ModelSerializer):
    """Serializer spécialement pour l'upload de CV"""
    cv_file = serializers.FileField(required=True)

    class Meta:
        model = Candidate
        fields = ['cv_file']

    def create(self, validated_data):
        """Créer un candidat avec valeurs par défaut"""
        cv_file = validated_data['cv_file']

        # Générer un email temporaire unique si nécessaire
        temp_email = f"temp_{timezone.now().timestamp()}@upload.temp"

        candidate = Candidate.objects.create(
            first_name='N/A',
            last_name='N/A',
            email=temp_email,
            phone='N/A',
            gender='N/A',
            address='N/A',
            city='N/A',
            education_level='N/A',
            cv_file=cv_file,
            cv_file_path=cv_file.name,  # Enregistrer le chemin
            status='pending_extraction',
            is_extracted=False
        )

        return candidate


class CandidateCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour création et modification des candidats"""

    class Meta:
        model = Candidate
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'gender',
            'birth_date', 'address', 'city', 'linkedin_url',
            'technical_skills', 'soft_skills', 'experience_years',
            'education_level', 'languages', 'status', 'ai_summary'
        ]

    def validate_email(self, value):
        """Validation de l'email avec vérification d'unicité"""
        if value:
            # Vérifier l'unicité sauf pour l'instance actuelle
            queryset = Candidate.objects.filter(email=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError("Un candidat avec cet email existe déjà.")
        return value

    def validate_technical_skills(self, value):
        """Validation des compétences techniques"""
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Les compétences techniques doivent être une liste.")
        return value or []

    def validate_soft_skills(self, value):
        """Validation des compétences soft"""
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Les soft skills doivent être une liste.")
        return value or []

    def validate_languages(self, value):
        """Validation des langues"""
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Les langues doivent être une liste.")
        return value or []

    def validate_experience_years(self, value):
        """Validation des années d'expérience"""
        if value is not None and (value < 0 or value > 70):
            raise serializers.ValidationError("Les années d'expérience doivent être entre 0 et 70.")
        return value

class CandidatePendingSerializer(serializers.ModelSerializer):
    """Serializer pour les candidats en attente d'extraction"""
    full_name = serializers.ReadOnlyField()
    cv_file_url = serializers.SerializerMethodField()
    upload_date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id', 'full_name', 'cv_file', 'cv_file_path', 'cv_file_url',
            'status', 'is_extracted', 'upload_date', 'created_at'
        ]

    def get_cv_file_url(self, obj):
        if obj.cv_file:
            return obj.cv_file.url
        return None


class CandidateMatchingSerializer(BaseCandidateSerializer):
    """Pour les résultats de matching - optimisé pour les scores"""
    matching_score = serializers.SerializerMethodField()
    matching_details = serializers.SerializerMethodField()
    recommendation = serializers.SerializerMethodField()
    embeddings_available = serializers.SerializerMethodField()

    class Meta(BaseCandidateSerializer.Meta):
        fields = [
            'id', 'full_name', 'email', 'phone', 'city',
            'experience_years', 'education_level', 'linkedin_url',
            'technical_skills', 'soft_skills',
            'matching_score', 'matching_details', 'recommendation',
            'embeddings_available'
        ]

    def get_matching_score(self, obj):
        return getattr(obj, '_matching_score', None)

    def get_matching_details(self, obj):
        return getattr(obj, '_matching_details', {})

    def get_recommendation(self, obj):
        return getattr(obj, '_recommendation', 'No analysis')

    def get_embeddings_available(self, obj):
        return obj.has_embeddings()


class CandidateEmbeddingsSerializer(serializers.ModelSerializer):
    """Serializer spécialisé pour les embeddings"""
    embeddings_sections = serializers.SerializerMethodField()
    embeddings_stats = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id', 'full_name', 'cv_embeddings', 'embeddings_generated_at',
            'embeddings_sections', 'embeddings_stats'
        ]

    def get_embeddings_sections(self, obj):
        """Liste des sections disponibles dans les embeddings"""
        if not obj.cv_embeddings:
            return []
        return list(obj.cv_embeddings.keys())

    def get_embeddings_stats(self, obj):
        """Statistiques sur les embeddings"""
        if not obj.cv_embeddings:
            return {'total_sections': 0, 'total_vectors': 0}

        total_vectors = sum(
            len(vectors) if isinstance(vectors, list) else 0
            for vectors in obj.cv_embeddings.values()
        )

        return {
            'total_sections': len(obj.cv_embeddings),
            'total_vectors': total_vectors,
            'generated_at': obj.embeddings_generated_at
        }


class JobOfferBaseSerializer(serializers.ModelSerializer):
    """Serializer de base pour JobOffer"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = JobOffer
        fields = [
            'id', 'title', 'description', 'requirements', 'benefits',
            'experience_level', 'contract_type', 'remote_allowed', 'status',
            'company', 'company_name', 'created_by', 'created_by_name',
            'created_at', 'deadline', 'matching_weights', 'system_prompt'
        ]
        read_only_fields = ['created_by', 'company']

    def validate_matching_weights(self, value):
        """Validation des poids de matching"""
        if not value:
            return value

        valid_fields = {'technical_skills', 'soft_skills', 'experience', 'education'}

        # Vérifier que tous les champs sont valides
        invalid_fields = set(value.keys()) - valid_fields
        if invalid_fields:
            raise serializers.ValidationError(
                f"Champs invalides dans matching_weights: {invalid_fields}. "
                f"Champs autorisés: {valid_fields}"
            )

        # Vérifier que les valeurs sont des nombres positifs
        for field, weight in value.items():
            if not isinstance(weight, (int, float)) or weight < 0:
                raise serializers.ValidationError(
                    f"Le poids pour '{field}' doit être un nombre positif"
                )

        # Vérifier que la somme n'est pas nulle
        if sum(value.values()) == 0:
            raise serializers.ValidationError(
                "La somme des poids ne peut pas être nulle"
            )

        return value


class JobOfferListSerializer(JobOfferBaseSerializer):
    """Pour la liste des offres - données résumées"""
    applications_count = serializers.SerializerMethodField()
    top_match_score = serializers.SerializerMethodField()

    class Meta(JobOfferBaseSerializer.Meta):
        fields = JobOfferBaseSerializer.Meta.fields + [
            'applications_count', 'top_match_score'
        ]

    def get_applications_count(self, obj):
        return getattr(obj, 'applications_count', 0)

    def get_top_match_score(self, obj):
        return getattr(obj, 'top_match_score', None)

    def get_has_custom_matching(self, obj):
        """Indique si cette offre utilise des paramètres de matching personnalisés"""
        return bool(obj.matching_weights or obj.system_prompt)


class JobOfferDetailSerializer(JobOfferBaseSerializer):
    """Pour le détail d'une offre - toutes les données"""
    recent_applications = serializers.SerializerMethodField()
    matching_stats = serializers.SerializerMethodField()
    ai_flags = serializers.SerializerMethodField()
    # Ces champs sont des SerializerMethodField car ils sont calculés
    effective_matching_weights = serializers.SerializerMethodField()
    effective_system_prompt = serializers.SerializerMethodField()

    class Meta(JobOfferBaseSerializer.Meta):
        fields = JobOfferBaseSerializer.Meta.fields + [
            'recent_applications', 'matching_stats', 'ai_flags',
            'ai_generated', 'seo_optimized', 'bias_checked',
            'effective_matching_weights', 'effective_system_prompt'
        ]

    def get_recent_applications(self, obj):
        recent = getattr(obj, 'recent_apps_prefetch',
                         obj.applications.select_related('candidate')[:10])

        return [{
            'id': app.id,
            'candidate_name': app.candidate.full_name,
            'candidate_email': app.candidate.email,
            'status': app.status,
            'match_score': app.ai_match_score,
            'applied_at': app.applied_at
        } for app in recent]

    def get_matching_stats(self, obj):
        # Stats depuis le cache de matching
        from django.db import models
        # Uncomment when MatchingCache model is available
        # from recruitment.models import MatchingCache

        # cache_stats = MatchingCache.objects.filter(
        #     job_offer=obj, is_valid=True
        # ).aggregate(
        #     count=models.Count('id'),
        #     avg_score=models.Avg('overall_score'),
        #     excellent_count=models.Count('id', filter=models.Q(overall_score__gte=0.8))
        # )

        # For now, return mock data until MatchingCache is implemented
        cache_stats = {
            'count': 0,
            'avg_score': 0,
            'excellent_count': 0
        }

        return {
            'total_candidates_analyzed': cache_stats['count'] or 0,
            'average_match_score': round((cache_stats['avg_score'] or 0) * 100, 1),
            'excellent_matches': cache_stats['excellent_count'] or 0
        }

    def get_ai_flags(self, obj):
        return {
            'ai_generated': obj.ai_generated,
            'seo_optimized': obj.seo_optimized,
            'bias_checked': obj.bias_checked
        }

    def get_effective_matching_weights(self, obj):
        """Retourne les poids effectifs utilisés (personnalisés ou par défaut)"""
        return obj.get_matching_weights()

    def get_effective_system_prompt(self, obj):
        """Retourne le prompt système effectif utilisé"""
        return obj.get_system_prompt()

class JobOfferMatchingConfigSerializer(serializers.ModelSerializer):
    """Serializer spécialisé pour la configuration du matching"""
    effective_weights = serializers.SerializerMethodField()
    weights_customized = serializers.SerializerMethodField()
    prompt_customized = serializers.SerializerMethodField()

    class Meta:
        model = JobOffer
        fields = [
            'id', 'title', 'matching_weights', 'system_prompt',
            'effective_weights', 'weights_customized', 'prompt_customized'
        ]

    def get_effective_weights(self, obj):
        return obj.get_matching_weights()

    def get_weights_customized(self, obj):
        return bool(obj.matching_weights)

    def get_prompt_customized(self, obj):
        return bool(obj.system_prompt)
class ApplicationUnifiedSerializer(serializers.ModelSerializer):
    """Serializer unifié pour Application"""
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    job_title = serializers.CharField(source='job_offer.title', read_only=True)
    company_name = serializers.CharField(source='job_offer.company.name', read_only=True)

    # Champs calculés pour le matching
    match_quality = serializers.SerializerMethodField()
    match_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'candidate', 'candidate_name', 'candidate_email',
            'job_offer', 'job_title', 'company_name',
            'status', 'ai_match_score', 'match_quality', 'match_breakdown',
            'ai_analysis', 'applied_at', 'last_updated'
        ]

    def get_match_quality(self, obj):
        score = obj.ai_match_score
        if score is None:
            return 'pending'
        elif score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'poor'

    def get_match_breakdown(self, obj):
        if obj.ai_analysis and isinstance(obj.ai_analysis, dict):
            breakdown = obj.ai_analysis.get('breakdown', {})
            return {
                field: {
                    'score': round(score * 100, 1) if isinstance(score, (int, float)) else score,
                    'status': 'excellent' if isinstance(score, (int, float)) and score >= 0.8
                    else 'good' if isinstance(score, (int, float)) and score >= 0.6
                    else 'fair' if isinstance(score, (int, float)) and score >= 0.4
                    else 'poor'
                } for field, score in breakdown.items()
            }
        return {}


class InterviewUnifiedSerializer(serializers.ModelSerializer):
    """Serializer unifié pour Interview"""
    candidate_name = serializers.CharField(source='application.candidate.full_name', read_only=True)
    candidate_email = serializers.CharField(source='application.candidate.email', read_only=True)
    job_title = serializers.CharField(source='application.job_offer.title', read_only=True)
    match_score = serializers.DecimalField(source='application.ai_match_score',
                                           max_digits=5, decimal_places=1, read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'candidate_name', 'candidate_email',
            'job_title', 'match_score', 'interview_type',
            'scheduled_at', 'interviewer', 'notes', 'created_at'
        ]


class MatchingCacheSerializer(serializers.ModelSerializer):
    """Serializer pour les données de cache de matching"""
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='job_offer.title', read_only=True)
    company_name = serializers.CharField(source='job_offer.company.name', read_only=True)
    score_percentage = serializers.SerializerMethodField()

    class Meta:
        model = MatchingCache
        fields = [
            'id', 'candidate', 'candidate_name', 'job_offer',
            'job_title', 'company_name', 'overall_score', 'score_percentage',
            'recommendation', 'detailed_scores', 'calculated_at', 'is_valid'
        ]

    def get_score_percentage(self, obj):
        return round(obj.overall_score * 100, 1)


class CandidateNoteSerializer(serializers.ModelSerializer):
    """Serializer pour les notes de candidat"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = CandidateNote
        fields = ['id', 'content', 'note_type', 'author', 'author_name', 'created_at']
        read_only_fields = ['author']


# ==========================================
# Serializers spécialisés pour les réponses API
# ==========================================

class MatchingResultSerializer(serializers.Serializer):
    """Serializer pour les résultats de matching unifiés"""
    success = serializers.BooleanField()
    entity_id = serializers.IntegerField()
    entity_name = serializers.CharField()
    entity_type = serializers.ChoiceField(choices=['candidate', 'job'])
    total_matches = serializers.IntegerField()
    processing_time = serializers.FloatField()
    matches = serializers.ListField()
    filters_applied = serializers.DictField()
    generated_at = serializers.DateTimeField()


class BatchMatchingResultSerializer(serializers.Serializer):
    """Serializer pour les résultats de matching par lot"""
    success = serializers.BooleanField()
    total_processed = serializers.IntegerField()
    successful_matches = serializers.IntegerField()
    failed_matches = serializers.IntegerField()
    processing_time = serializers.FloatField()
    results = serializers.ListField()
    errors = serializers.ListField()


class MatchingAnalyticsSerializer(serializers.Serializer):
    """Serializer pour les analytics de matching"""
    overview = serializers.DictField()
    score_distribution = serializers.DictField()
    top_skills = serializers.DictField()
    recent_activity = serializers.DictField()
    performance_metrics = serializers.DictField()
    generated_at = serializers.DateTimeField()

class GroupCandidateBaseSerializer(serializers.ModelSerializer):
    """Serializer de base pour GroupCandidate - sans référence company"""
    candidats_count = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = GroupCandidate
        fields = [
            'id', 'nom', 'description', 'type_groupe', 'couleur',
            'ordre_affichage', 'is_active', 'is_public', 'auto_populate',
            'candidats_count', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'last_sync'
        ]
        read_only_fields = ['created_by']

class CandidatGroupeMembershipSerializer(serializers.Serializer):
    """Pour gérer l'appartenance aux groupes - sans company"""
    candidat_id = serializers.IntegerField()
    groupe_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Liste des IDs des groupes"
    )
    action = serializers.ChoiceField(
        choices=['add', 'remove', 'replace'],
        default='replace',
        help_text="Action à effectuer: add (ajouter), remove (retirer), replace (remplacer)"
    )

    def validate_candidat_id(self, value):
        """Vérifier que le candidat existe"""
        try:
            from .models import Candidate
            Candidate.objects.get(id=value)
            return value
        except Candidate.DoesNotExist:
            raise serializers.ValidationError("Candidat introuvable")

    def validate_groupe_ids(self, value):
        """Vérifier que tous les groupes existent et appartiennent à l'utilisateur"""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Utilisateur invalide")

        groupes = GroupCandidate.objects.filter(
            id__in=value,
            created_by=request.user
        )

        if len(groupes) != len(value):
            missing_ids = set(value) - set(groupes.values_list('id', flat=True))
            raise serializers.ValidationError(
                f"Groupes introuvables ou non autorisés: {missing_ids}"
            )

        return value


class GroupCandidateListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des groupes de candidats"""
    candidats_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = GroupCandidate
        fields = [
            'id', 'nom', 'description', 'type_groupe', 'couleur',
            'ordre_affichage', 'is_active', 'is_public',
            'candidats_count', 'created_by_name', 'created_at', 'updated_at'
        ]

    def get_candidats_count(self, obj):
        # Try to get from annotation first, fallback to method
        return getattr(obj, 'candidats_count_annotated', obj.get_candidats_count())


class GroupCandidateSummarySerializer(serializers.ModelSerializer):
    """Serializer résumé pour les sélections de groupes"""
    candidats_count = serializers.SerializerMethodField()

    class Meta:
        model = GroupCandidate
        fields = ['id', 'nom', 'couleur', 'type_groupe', 'candidats_count']

    def get_candidats_count(self, obj):
        # Try to get from annotation first, fallback to method
        return getattr(obj, 'candidats_count_annotated', obj.get_candidats_count())


class GroupCandidateDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un groupe de candidats"""
    candidats_count = serializers.SerializerMethodField()
    candidats_details = serializers.SerializerMethodField()
    skills_distribution = serializers.ReadOnlyField()
    experience_distribution = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = GroupCandidate
        fields = [
            'id', 'nom', 'description', 'type_groupe', 'couleur',
            'ordre_affichage', 'is_active', 'is_public',
            'candidats_count', 'candidats_details',
            'skills_distribution', 'experience_distribution',
            'auto_populate', 'criteria_json',
            'created_by', 'created_by_name',
            'created_at', 'updated_at', 'last_sync'
        ]

    def get_candidats_count(self, obj):
        return getattr(obj, 'candidats_count_annotated', obj.get_candidats_count())

    def get_candidats_details(self, obj):
        """Détails des candidats du groupe (limité pour performance)"""
        candidats = obj.candidats.all()[:20]  # Limite pour éviter la surcharge
        return [{
            'id': c.id,
            'full_name': c.full_name,
            'email': c.email,
            'city': c.city,
            'experience_years': c.experience_years,
            'status': c.status,
            'created_at': c.created_at
        } for c in candidats]


class GroupCandidateCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour création/mise à jour des groupes"""

    class Meta:
        model = GroupCandidate
        fields = [
            'nom', 'description', 'type_groupe', 'couleur',
            'ordre_affichage', 'is_active', 'is_public',
            'auto_populate', 'criteria_json'
        ]

    def validate_nom(self, value):
        """Validation du nom de groupe"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du groupe est requis")

        # Vérifier l'unicité pour l'utilisateur
        request = self.context.get('request')
        if request and request.user:
            existing = GroupCandidate.objects.filter(
                nom=value.strip(),
                created_by=request.user
            )

            # Exclure l'instance actuelle lors de la mise à jour
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError(
                    "Un groupe avec ce nom existe déjà pour votre compte"
                )

        return value.strip()

    def validate_criteria_json(self, value):
        """Validation des critères automatiques"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Les critères doivent être un objet JSON valide")
        return value