from rest_framework import serializers

from .models import (
    Activity,
    ActivityMemo,
    ActivityCategory,
    Tag,
    ActivityRole,
    Career,
    Award,
    Certification,
    GlobalExp,
    ForeignLang,
    ActivityHardSkill,
    ActivitySoftSkill,
    SubActivity,
)
from apps.profiles.models import HardSkill, SoftSkill
from apps.dashboard.models import ExperienceNote


# ---- 기본 ----
class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = ["id", "key", "name", "order"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "kind"]


class ActivityMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMemo
        fields = ["id", "content", "date"]
        read_only_fields = ["id", "date"]


class ActivityRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRole
        fields = ["id", "name", "count"]


class SubActivitySerializer(serializers.ModelSerializer):
    """
    활동 상세 화면의 '포함된 활동' 카드 한 개에 해당하는 세부 활동.
    """

    class Meta:
        model = SubActivity
        fields = [
            "id",
            "title",
            "summary",
            "period_start",
            "period_end",
            "is_ongoing",
            "metric",
            "hard_tools",
            "soft_skills",
            "situation",
            "task_detail",
            "action_detail",
            "result_detail",
            "takeaway",
            "attachment",
            "link_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---- Activity ----
class ActivitySerializer(serializers.ModelSerializer):
    category = ActivityCategorySerializer(read_only=True)
    experience_notes = serializers.SerializerMethodField(read_only=True)
    sub_activities = SubActivitySerializer(many=True, read_only=True)

    # 쓰기용 필드들 (응답에는 포함되지만, 의미상 입력용)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ActivityCategory.objects.filter(is_active=True),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    primary_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    secondary_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    role_items = ActivityRoleSerializer(
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Activity
        fields = [
            "id",
            # 상단 기본 정보
            "title",
            "period_start",
            "period_end",
            "organization",
            "host",
            "subject",
            "role",
            "work_title",
            "participation_type",
            "is_awarded",
            "award_detail",
            # 세부 내용 (Situation / Task / Action / Result / Taken)
            "situation",
            "task_detail",
            "action_detail",
            "result_detail",
            "takeaway",
            # 첨부 / 링크
            "attachment",
            "link_url",
            # 활동 종류(프로젝트/공모전/교내활동 등)
            "category",
            "category_id",
            # 태그 / 역할 (작성용)
            "tag_ids",
            "primary_tag_ids",
            "secondary_tag_ids",
            "role_items",
            # 경험 노트 / 포함된 활동
            "experience_notes",
            "sub_activities",
        ]
        read_only_fields = [
            "id",
            "category",
            "experience_notes",
            "sub_activities",
        ]

    def _save_roles(self, activity, validated_data):
        role_items = validated_data.pop("role_items", None)
        if role_items is not None:
            activity.roles.all().delete()
            ActivityRole.objects.bulk_create(
                [ActivityRole(activity=activity, **item) for item in role_items]
            )

    def _save_tags(self, activity, validated_data, *, on_create=False):
        primary = validated_data.pop("primary_tag_ids", None)
        secondary = validated_data.pop("secondary_tag_ids", None)
        flat = validated_data.pop("tag_ids", None)

        if primary is not None or secondary is not None:
            primary = list(primary or [])
            secondary = list(secondary or [])
            activity.primary_tags.set(primary)
            activity.secondary_tags.set(secondary)

            union_ids = {t.id for t in primary} | {t.id for t in secondary}
            if union_ids:
                activity.tags.set(Tag.objects.filter(id__in=union_ids))
            elif on_create:
                activity.tags.clear()
        elif flat is not None:
            activity.tags.set(flat)

    def create(self, validated_data):
        role_items = validated_data.pop("role_items", None)
        tags_payload = {
            "primary_tag_ids": validated_data.pop("primary_tag_ids", None),
            "secondary_tag_ids": validated_data.pop("secondary_tag_ids", None),
            "tag_ids": validated_data.pop("tag_ids", None),
        }
        activity = Activity.objects.create(**validated_data)
        self._save_tags(activity, tags_payload, on_create=True)
        if role_items is not None:
            activity.roles.all().delete()
            ActivityRole.objects.bulk_create(
                [ActivityRole(activity=activity, **item) for item in role_items]
            )
        return activity

    def update(self, instance, validated_data):
        activity = super().update(instance, validated_data)
        self._save_tags(activity, validated_data)
        self._save_roles(activity, validated_data)
        return activity

    def get_experience_notes(self, obj):
        """
        이 활동과 연결된 경험 노트 목록을 간단한 형태로 반환.
        """
        notes = (
            ExperienceNote.objects.filter(user=obj.user, activity=obj)
            .order_by("-date", "-updated_at")
        )
        return [
            {
                "id": note.id,
                "date": note.date.isoformat(),
                "content": note.content,
            }
            for note in notes
        ]


# ---- Award / Certification / Career ----
class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = "__all__"
        read_only_fields = ["id", "user"]


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"
        read_only_fields = ["id", "user"]


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = "__all__"
        read_only_fields = ["id", "user"]


# ---- GlobalExp / ForeignLang ----
class GlobalExpSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalExp
        fields = "__all__"
        read_only_fields = ["id", "user"]


class ForeignLangSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForeignLang
        fields = "__all__"
        read_only_fields = ["id", "user"]


# ---- Activity Skill 링크 ----
class ActivityHardSkillSerializer(serializers.ModelSerializer):
    hard_skill = serializers.SerializerMethodField(read_only=True)
    hard_skill_id = serializers.PrimaryKeyRelatedField(
        queryset=HardSkill.objects.all(),
        source="hard_skill",
        write_only=True,
    )

    class Meta:
        model = ActivityHardSkill
        fields = ["id", "activity", "hard_skill", "hard_skill_id", "level", "level_description"]
        read_only_fields = ["id", "activity", "hard_skill"]

    def get_hard_skill(self, obj):
        return {
            "id": obj.hard_skill.id,
            "name": obj.hard_skill.name,
            "code": obj.hard_skill.code,
        }


class ActivitySoftSkillSerializer(serializers.ModelSerializer):
    soft_skill = serializers.SerializerMethodField(read_only=True)
    soft_skill_id = serializers.PrimaryKeyRelatedField(
        queryset=SoftSkill.objects.all(),
        source="soft_skill",
        write_only=True,
    )

    class Meta:
        model = ActivitySoftSkill
        fields = ["id", "activity", "soft_skill", "soft_skill_id", "level", "level_description"]
        read_only_fields = ["id", "activity", "soft_skill"]

    def get_soft_skill(self, obj):
        return {"id": obj.soft_skill.id, "name": obj.soft_skill.name}
