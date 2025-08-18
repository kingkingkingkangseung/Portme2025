from rest_framework import serializers
from .models import Activity, ActivityMemo, ActivityCategory, Tag

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

class ActivitySerializer(serializers.ModelSerializer):
    # 읽기용
    memos = ActivityMemoSerializer(many=True, read_only=True)
    category = ActivityCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    # 쓰기용
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

    class Meta:
        model = Activity
        fields = [
            "id",
            "title", "period_start", "period_end",
            "role", "description", "outcome",
            "attachment",
            # ⬇️ 추가된 부분
            "category", "category_id",
            "tags", "tag_ids",
            "created_at", "updated_at",
            "memos",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "memos", "category", "tags"]

    def create(self, validated_data):
        tag_objs = validated_data.pop("tag_ids", [])
        activity = super().create(validated_data)
        if tag_objs:
            activity.tags.set(tag_objs)
        return activity

    def update(self, instance, validated_data):
        tag_objs = validated_data.pop("tag_ids", None)
        activity = super().update(instance, validated_data)
        if tag_objs is not None:
            activity.tags.set(tag_objs)
        return activity
