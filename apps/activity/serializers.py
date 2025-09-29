from rest_framework import serializers
from .models import (
    Activity, ActivityMemo, ActivityCategory, Tag,
    ActivityRole, Award, Certification, ForeignLang, GlobalExp
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

    class Meta:
        model = Activity
        fields = "__all__"
        read_only_fields = [
            "id", "created_at", "updated_at",
            "memos", "category", "tags", "roles",
            "primary_tags", "secondary_tags",
        ]


# ---- Award / Certification / ForeignLang / GlobalExp ----
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


class ForeignLangSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForeignLang
        fields = "__all__"
        read_only_fields = ["id", "user"]


class GlobalExpSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalExp
        fields = "__all__"
        read_only_fields = ["id", "user"]
