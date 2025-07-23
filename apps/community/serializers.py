from rest_framework import serializers
from .models import Post, Comment

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "user_name", "content", "is_answer",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "user", "user_name", "is_answer",
                            "created_at", "updated_at"]


class PostListSerializer(serializers.ModelSerializer):
    user_name   = serializers.CharField(source="user.username", read_only=True)
    comment_cnt = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "type", "title", "category", "tags",
                  "user_name", "comment_cnt", "like_count", "view_count",
                  "created_at"]
        

class PostDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    comments  = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "type", "title", "content", "category", "tags",
                  "user_name", "like_count", "view_count",
                  "created_at", "updated_at",
                  "comments"]
        read_only_fields = ["id", "user_name", "like_count", "view_count",
                            "created_at", "updated_at", "comments"]
