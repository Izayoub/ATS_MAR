from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from recruitment.models import JobOffer, Application, Candidate
from .models import RecruitmentMetric, DashboardWidget
from .serializers import RecruitmentMetricSerializer, DashboardWidgetSerializer


class AnalyticsViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def dashboard_overview(self, request):
        """Vue d'ensemble du dashboard"""
        company = request.user.company

        # Période (30 derniers jours par défaut)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Statistiques de base
        stats = {
            'total_jobs': JobOffer.objects.filter(company=company).count(),
            'active_jobs': JobOffer.objects.filter(company=company, status='active').count(),
            'total_applications': Application.objects.filter(job_offer__company=company).count(),
            'total_candidates': Candidate.objects.count(),
            'applications_this_month': Application.objects.filter(
                job_offer__company=company,
                applied_at__date__gte=start_date
            ).count()
        }

        # Pipeline de recrutement
        pipeline = {}
        for status_code, status_label in Application.STATUS_CHOICES:
            pipeline[status_code] = {
                'label': status_label,
                'count': Application.objects.filter(
                    job_offer__company=company,
                    status=status_code
                ).count()
            }

        # Top 5 des postes avec le plus de candidatures
        top_jobs = JobOffer.objects.filter(company=company).annotate(
            applications_count=Count('application')
        ).order_by('-applications_count')[:5]

        top_jobs_data = []
        for job in top_jobs:
            top_jobs_data.append({
                'id': job.id,
                'title': job.title,
                'applications_count': job.applications_count,
                'status': job.status
            })

        # Évolution des candidatures (7 derniers jours)
        applications_trend = []
        for i in range(7):
            date = end_date - timedelta(days=i)
            count = Application.objects.filter(
                job_offer__company=company,
                applied_at__date=date
            ).count()
            applications_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })

        return Response({
            'success': True,
            'stats': stats,
            'pipeline': pipeline,
            'top_jobs': top_jobs_data,
            'applications_trend': list(reversed(applications_trend))
        })

    @action(detail=False, methods=['get'])
    def recruitment_funnel(self, request):
        """Analyse du funnel de recrutement"""
        company = request.user.company

        # Calculer les taux de conversion
        total_applications = Application.objects.filter(job_offer__company=company).count()

        funnel_data = []
        previous_count = total_applications

        # Étapes du funnel
        funnel_steps = [
            ('received', 'Candidatures reçues'),
            ('screening', 'Pré-sélection'),
            ('interview', 'Entretiens'),
            ('tests', 'Tests techniques'),
            ('final', 'Entretiens finaux'),
            ('accepted', 'Acceptés')
        ]

        for status_code, status_label in funnel_steps:
            if status_code == 'received':
                count = total_applications
            else:
                count = Application.objects.filter(
                    job_offer__company=company,
                    status=status_code
                ).count()

            conversion_rate = (count / previous_count * 100) if previous_count > 0 else 0

            funnel_data.append({
                'step': status_code,
                'label': status_label,
                'count': count,
                'conversion_rate': round(conversion_rate, 1)
            })

            previous_count = count

        return Response({
            'success': True,
            'funnel': funnel_data
        })

    @action(detail=False, methods=['get'])
    def ai_insights(self, request):
        """Insights basés sur l'IA"""
        company = request.user.company

        # Analyse des scores de matching
        applications_with_scores = Application.objects.filter(
            job_offer__company=company,
            ai_match_score__isnull=False
        )

        if applications_with_scores.exists():
            avg_match_score = applications_with_scores.aggregate(
                avg_score=Avg('ai_match_score')
            )['avg_score']

            # Distribution des scores
            score_distribution = {
                'excellent': applications_with_scores.filter(ai_match_score__gte=80).count(),
                'good': applications_with_scores.filter(ai_match_score__gte=60, ai_match_score__lt=80).count(),
                'average': applications_with_scores.filter(ai_match_score__gte=40, ai_match_score__lt=60).count(),
                'poor': applications_with_scores.filter(ai_match_score__lt=40).count()
            }

            # Corrélation score IA vs succès recrutement
            accepted_apps = applications_with_scores.filter(status='accepted')
            avg_accepted_score = accepted_apps.aggregate(
                avg_score=Avg('ai_match_score')
            )['avg_score'] or 0

        else:
            avg_match_score = 0
            score_distribution = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
            avg_accepted_score = 0

        # Recommandations IA
        recommendations = []

        if avg_match_score < 50:
            recommendations.append({
                'type': 'warning',
                'message': 'Score de matching moyen faible. Considérez réviser vos critères de sélection.',
                'action': 'Optimiser les descriptions de postes'
            })

        if score_distribution['poor'] > score_distribution['excellent']:
            recommendations.append({
                'type': 'info',
                'message': 'Beaucoup de candidatures avec scores faibles. Améliorer le sourcing.',
                'action': 'Revoir les canaux de recrutement'
            })

        return Response({
            'success': True,
            'ai_insights': {
                'avg_match_score': round(avg_match_score, 1),
                'score_distribution': score_distribution,
                'avg_accepted_score': round(avg_accepted_score, 1),
                'recommendations': recommendations
            }
        })


class RecruitmentMetricViewSet(viewsets.ModelViewSet):
    queryset = RecruitmentMetric.objects.all()
    serializer_class = RecruitmentMetricSerializer

    def get_queryset(self):
        return RecruitmentMetric.objects.filter(company=self.request.user.company)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer

    def get_queryset(self):
        return DashboardWidget.objects.filter(user=self.request.user)