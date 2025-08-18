from rest_framework import serializers
from .models import Post, Comment
from apps.activity.models import Tag, Activity

# ── Nested serializers (읽기용) ─────────────────────────────────────
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "kind"]

class ActivityMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "title"]

# ── Comment ─────────────────────────────────────────────────────────
class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "user_name", "content", "is_answer", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "user_name", "is_answer", "created_at", "updated_at"]

# ── Post List ───────────────────────────────────────────────────────
class PostListSerializer(serializers.ModelSerializer):
    user_name   = serializers.CharField(source="user.username", read_only=True)
    comment_cnt = serializers.IntegerField(source="comments.count", read_only=True)
    likes_count  = serializers.IntegerField(source="likes.count",  read_only=True)
    scraps_count = serializers.IntegerField(source="scraps.count", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "type", "title", "category",
            "tags",
            "user_name", "comment_cnt",
            "likes_count", "scraps_count",
            "view_count", "created_at", "updated_at",
        ]

# ── Post Detail ─────────────────────────────────────────────────────
class PostDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    comments  = CommentSerializer(many=True, read_only=True)
    likes_count  = serializers.IntegerField(source="likes.count",  read_only=True)
    scraps_count = serializers.IntegerField(source="scraps.count", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    activities = ActivityMiniSerializer(many=True, read_only=True)

    # 쓰기용
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )
    activity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Post
        fields = [
            "id", "type", "title", "content", "category",
            "visibility",
            "tags", "tag_ids",
            "activities", "activity_ids",
            "user_name",
            "likes_count", "scraps_count",
            "view_count", "created_at", "updated_at",
            "comments",
        ]
        read_only_fields = [
            "id", "user_name",
            "likes_count", "scraps_count",
            "view_count", "created_at", "updated_at",
            "comments", "tags", "activities",
        ]

    def create(self, validated_data):
        tag_objs = validated_data.pop("tag_ids", [])
        act_objs = validated_data.pop("activity_ids", [])
        post = super().create(validated_data)
        if tag_objs:
            post.tags.set(tag_objs)
        if act_objs:
            post.activities.set(act_objs)
        return post

    def update(self, instance, validated_data):
        tag_objs = validated_data.pop("tag_ids", None)
        act_objs = validated_data.pop("activity_ids", None)
        post = super().update(instance, validated_data)
        if tag_objs is not None:
            post.tags.set(tag_objs)
        if act_objs is not None:
            post.activities.set(act_objs)
        return post
