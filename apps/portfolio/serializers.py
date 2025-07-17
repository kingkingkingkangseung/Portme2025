from rest_framework import serializers
from .models import Portfolio
from apps.activity.serializers import ActivitySerializer

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'concept_line', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortfolioDetailSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'concept_line',
            'activities',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']