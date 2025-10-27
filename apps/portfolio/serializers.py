from rest_framework import serializers
from .models import Portfolio, Project, ProjectCategory
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


# ---------- ERD 확장: 프로젝트 ----------

class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ["id", "code", "name", "order"]


class ProjectSerializer(serializers.ModelSerializer):
    category = ProjectCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProjectCategory.objects.filter(is_active=True),
        source='category', write_only=True, required=False, allow_null=True
    )
    activities = ActivitySerializer(many=True, read_only=True)
    activity_ids = serializers.PrimaryKeyRelatedField(
        queryset=None, many=True, write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'period_start', 'period_end',
            'position', 'category', 'category_id',
            'activities', 'activity_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'activities', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 지연 import로 순환참조 회피
        from apps.activity.models import Activity
        self.fields['activity_ids'].queryset = Activity.objects.all()

    def create(self, validated_data):
        acts = validated_data.pop('activity_ids', [])
        project = Project.objects.create(**validated_data)
        if acts:
            project.activities.set(acts)
        return project

    def update(self, instance, validated_data):
        acts = validated_data.pop('activity_ids', None)
        project = super().update(instance, validated_data)
        if acts is not None:
            project.activities.set(acts)
        return project
