from rest_framework import serializers
from .models import (
    Activity, ActivityMemo, ActivityCategory, Tag, ActivityRole,
    Award, Certification, GlobalExp, ForeignLang
)


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


# ---- Activity ----
class ActivitySerializer(serializers.ModelSerializer):
    memos = ActivityMemoSerializer(many=True, read_only=True)
    roles = ActivityRoleSerializer(many=True, read_only=True)
    category = ActivityCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    primary_tags = TagSerializer(many=True, read_only=True)
    secondary_tags = TagSerializer(many=True, read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ActivityCategory.objects.filter(is_active=True),
        source="category",
        write_only=True, required=False, allow_null=True,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )
    primary_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )
    secondary_tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )
    role_items = ActivityRoleSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Activity
        fields = [
            "id",
            "title", "period_start", "period_end", "organization",
            "plan_count", "design_count", "dev_count",
            "description", "role",
            "outcome", "learned",
            "attachment", "link_url",
            "category", "category_id",
            "tags", "tag_ids",
            "primary_tags", "secondary_tags",
            "primary_tag_ids", "secondary_tag_ids",
            "roles", "role_items",
            "created_at", "updated_at",
            "memos",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "memos", "category", "tags", "roles",
            "primary_tags", "secondary_tags",
        ]

    def _save_roles(self, activity, validated_data):
        role_items = validated_data.pop("role_items", None)
        if role_items is not None:
            activity.roles.all().delete()
            ActivityRole.objects.bulk_create([
                ActivityRole(activity=activity, **item) for item in role_items
            ])

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
        activity = Activity.objects.create(**validated_data)
        self._save_tags(activity, validated_data, on_create=True)
        self._save_roles(activity, validated_data)
        return activity

    def update(self, instance, validated_data):
        activity = super().update(instance, validated_data)
        self._save_tags(activity, validated_data)
        self._save_roles(activity, validated_data)
        return activity


# ---- Award / Certification ----
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
