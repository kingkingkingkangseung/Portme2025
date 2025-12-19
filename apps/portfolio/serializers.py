from rest_framework import serializers
from .models import Portfolio, Project, ProjectCategory
from apps.activity.serializers import ActivitySerializer
from apps.activity.models import Activity

class PortfolioSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, read_only=True)
    activity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Portfolio
        fields = [
            'id',
            'title',
            'selected_tags',
            'work_style',
            'strengths',
            'concept_line',
            'activities',
            'activity_ids',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'activities']

    def create(self, validated_data):
        acts = validated_data.pop('activity_ids', [])
        portfolio = Portfolio.objects.create(**validated_data)
        if acts:
            portfolio.activities.set(acts)
        return portfolio

    def update(self, instance, validated_data):
        acts = validated_data.pop('activity_ids', None)
        portfolio = super().update(instance, validated_data)
        if acts is not None:
            portfolio.activities.set(acts)
        return portfolio

    def validate(self, attrs):
        acts = attrs.get("activity_ids")
        request = self.context.get("request")
        if acts is not None and request is not None:
            invalid = [a.id for a in acts if a.user_id != request.user.id]
            if invalid:
                raise serializers.ValidationError({"activity_ids": "본인 활동만 선택할 수 있습니다."})
        return attrs


class PortfolioDetailSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            'id',
            'title',
            'selected_tags',
            'work_style',
            'strengths',
            'concept_line',
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
        queryset=Activity.objects.all(), many=True, write_only=True, required=False
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
