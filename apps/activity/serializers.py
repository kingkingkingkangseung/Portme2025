from django.apps import apps  # ⬅️ 새로 추가 (순환 import 피하려고)
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

    # ✅ 추가: 이 활동과 연결된 회고(간단 요약 리스트)
    retros = serializers.SerializerMethodField()

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
            "category", "category_id",
            "tags", "tag_ids",
            "created_at", "updated_at",
            "memos",
            "retros",                     # ⬅️ 여기에 포함
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "memos", "category", "tags", "retros"
        ]

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

    # ------------------------------
    # 🔥 역참조 회고 계산 필드
    # ------------------------------
    def get_retros(self, obj):
        """
        이 활동과 연결된 회고(Post.type='retro')를 간단 요약으로 반환.
        프라이버시를 위해 같은 소유자(user=obj.user)만 대상.
        """
        Post = apps.get_model("community", "Post")
        qs = (Post.objects
              .filter(type="retro", activities=obj, user=obj.user)
              .order_by("-created_at"))
        # 필요한 필드만 내려줌 (원하면 추가 가능: 'view_count', 'like_count' 등)
        return list(qs.values("id", "title", "created_at"))
