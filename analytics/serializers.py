from rest_framework import serializers
from .models import RecruitmentMetric, DashboardWidget

class RecruitmentMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentMetric
        fields = ['id', 'metric_type', 'value', 'period_start', 'period_end', 'metadata', 'created_at']

class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = ['id', 'widget_type', 'title', 'config', 'position_x', 'position_y', 'width', 'height', 'is_active']
