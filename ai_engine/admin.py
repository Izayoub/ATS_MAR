from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import MatchingLog, BatchMatchingLog
from .services.matching_service import django_matching


@admin.register(MatchingLog)
class MatchingLogAdmin(admin.ModelAdmin):
    list_display = ['cv_id', 'score', 'cv_domain', 'confidence', 'execution_time_ms', 'from_cache', 'created_at']
    list_filter = ['cv_domain', 'from_cache', 'created_at']
    search_fields = ['cv_id', 'job_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(BatchMatchingLog)
class BatchMatchingLogAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'total_cvs', 'qualified_cvs', 'avg_score', 'processing_time_ms', 'created_at']
    list_filter = ['created_at']
    search_fields = ['job_title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


class MatchingServiceAdmin(admin.ModelAdmin):
    """Admin personnalisé pour le service de matching"""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('service-status/', self.service_status_view, name='matching_service_status'),
            path('clear-cache/', self.clear_cache_view, name='matching_clear_cache'),
            path('test-service/', self.test_service_view, name='matching_test_service'),
        ]
        return custom_urls + urls

    def service_status_view(self, request):
        """Vue de statut du service"""
        status = django_matching_service.get_health_status()

        context = {
            'title': 'Statut Service Matching CV',
            'status': status,
            'has_permission': True,
            'opts': self.model._meta if hasattr(self, 'model') else None,
        }

        return render(request, 'admin/ai_engine/service_status.html', context)

    def clear_cache_view(self, request):
        """Vue pour vider le cache"""
        if request.method == 'POST':
            try:
                from django.core.cache import cache
                cache.clear()
                messages.success(request, "Cache du service de matching vidé avec succès")
            except Exception as e:
                messages.error(request, f"Erreur lors du vidage du cache: {e}")

        return HttpResponseRedirect('../service-status/')

    def test_service_view(self, request):
        """Vue de test rapide du service"""
        # CV de test
        test_cv = {
            "titre_candidat": "Développeur Python Test",
            "profil_resume": "Test automatique du service",
            "formations": ["Master"],
            "experience_years": 3,
            "competences_techniques": ["Python", "Django"],
            "competences_informatiques": ["Git"],
            "langues": ["Français"],
            "certifications": [],
            "projets": ["Test"],
            "soft_skills": ["teamwork"]
        }

        test_job = {
            "titre_poste": "Développeur Backend Test",
            "missions": "Test du service de matching",
            "exigences": {
                "formation_requise": "Bac+5",
                "annees_experience": 2,
                "competences_obligatoires": ["Python"],
                "competences_souhaitees": ["Django"],
                "langues": ["Français"],
                "certifications": [],
                "outils": ["Git"],
                "qualites_humaines": ["autonomie"]
            }
        }

        try:
            result = django_matching_service.match_cv_to_job(test_cv, test_job, "test_cv", use_cache=False)
            test_success = result.get('total_score', 0) > 0

            if test_success:
                messages.success(request, f"✅ Test réussi - Score: {result['total_score']}/100")
            else:
                messages.warning(request, f"⚠️ Test avec problème - Score: {result.get('total_score', 0)}")

        except Exception as e:
            messages.error(request, f"❌ Échec du test: {e}")

        return HttpResponseRedirect('../service-status/')

