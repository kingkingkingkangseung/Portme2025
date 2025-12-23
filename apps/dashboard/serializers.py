from rest_framework import serializers
from django.utils import timezone

from apps.dashboard.models import ExperienceNote, GoalVision
from apps.activity.models import Activity
from apps.portfolio.models import Project


class ExperienceNoteSerializer(serializers.ModelSerializer):
    activity_id = serializers.PrimaryKeyRelatedField(
        source="activity",
        queryset=Activity.objects.all(),
        allow_null=True,
        required=False,
    )
    project_id = serializers.PrimaryKeyRelatedField(
        source="project",
        queryset=Project.objects.all(),
        allow_null=True,
        required=False,
    )
    activity_title = serializers.CharField(source="activity.title", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = ExperienceNote
        fields = (
            "id",
            "date",
            "content",
            "activity_id",
            "project_id",
            "activity_title",
            "project_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "activity_title", "project_name")

    def validate(self, attrs):
        user = self.context["request"].user
        activity = attrs.get("activity")
        if activity and activity.user_id != user.id:
            raise serializers.ValidationError({"activity_id": "본인 경험만 연결할 수 있습니다."})
        project = attrs.get("project")
        if project and project.user_id != user.id:
            raise serializers.ValidationError({"project_id": "본인 프로젝트만 연결할 수 있습니다."})
        return attrs


class ActivityBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = (
            "id",
            "title",
            "activity_type",
            "organization",
            "period_start",
            "period_end",
            "status",
            "board_order",
            "plan_count",
            "design_count",
            "dev_count",
            "is_deleted",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class GoalVisionSerializer(serializers.ModelSerializer):
    goal = serializers.CharField(source="content", write_only=True, required=False, allow_blank=True)
    is_done = serializers.BooleanField(source="is_completed", write_only=True, required=False)

    class Meta:
        model = GoalVision
        fields = (
            "id",
            "content",
            "goal",
            "is_completed",
            "is_done",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
