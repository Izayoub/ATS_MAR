from django.db import models
from django.contrib.auth import get_user_model
from recruitment.models import JobOffer, Application

User = get_user_model()


class RecruitmentMetric(models.Model):
    METRIC_TYPES = [
        ('time_to_hire', 'Temps de recrutement'),
        ('source_performance', 'Performance source'),
        ('conversion_rate', 'Taux de conversion'),
        ('cost_per_hire', 'Coût par recrutement'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.FloatField()
    period_start = models.DateField()
    period_end = models.DateField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class DashboardWidget(models.Model):
    WIDGET_TYPES = [
        ('chart', 'Graphique'),
        ('counter', 'Compteur'),
        ('table', 'Tableau'),
        ('progress', 'Barre de progression'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    config = models.JSONField(default=dict)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)