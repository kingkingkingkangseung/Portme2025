# apps/community/serializers.py
from rest_framework import serializers
from .models import Post, Comment, Retro       # ✅ Retro import
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

# ✅ 회고 상세
class RetroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retro
        fields = [
            "retro_type",
            "date", "duration_minutes", "mood",
            "keep", "problem", "try_field",
            "objective", "fact", "result",
        ]


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

    # ✅ 회고 상세: 읽기용
    retro = RetroSerializer(read_only=True)

    # ✅ 회고 상세: 쓰기용 입력(JSON 객체로 받음)
    retro_input = RetroSerializer(write_only=True, required=False)

    # 쓰기용 M2M
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
            "retro", "retro_input",                # ✅ 추가
            "user_name",
            "likes_count", "scraps_count",
            "view_count", "created_at", "updated_at",
            "comments",
        ]
        read_only_fields = [
            "id", "user_name",
            "likes_count", "scraps_count",
            "view_count", "created_at", "updated_at",
            "comments", "tags", "activities", "retro",
        ]

    # 🔎 회고 유효성: type=retro면 retro_input 필수(최소한 retro_type & date)
    def validate(self, attrs):
        req = self.context.get("request")
        method = req.method if req else None

        # 생성 시에는 attrs에, 수정 시에는 partial일 수 있어서 유연하게 체크
        t = attrs.get("type") or getattr(getattr(self, "instance", None), "type", None)

        if t == "retro":
            retro_payload = attrs.get("retro_input")
            if method == "POST" and not retro_payload:
                raise serializers.ValidationError({"retro_input": "회고 데이터가 필요합니다."})
            if retro_payload:
                if not retro_payload.get("retro_type"):
                    raise serializers.ValidationError({"retro_input.retro_type": "필수입니다. (KPT|AAR)"})
                if not retro_payload.get("date"):
                    raise serializers.ValidationError({"retro_input.date": "필수입니다. (YYYY-MM-DD)"})
        else:
            # article/question/review 인 경우에는 retro_input이 와도 무시
            attrs.pop("retro_input", None)

        return attrs

    def create(self, validated_data):
        tag_objs = validated_data.pop("tag_ids", [])
        act_objs = validated_data.pop("activity_ids", [])
        retro_payload = validated_data.pop("retro_input", None)

        post = super().create(validated_data)

        if tag_objs:
            post.tags.set(tag_objs)
        if act_objs:
            post.activities.set(act_objs)

        # ✅ type=retro 이면 Retro 생성
        if post.type == "retro" and retro_payload:
            Retro.objects.create(post=post, **retro_payload)

        return post

    def update(self, instance, validated_data):
        tag_objs = validated_data.pop("tag_ids", None)
        act_objs = validated_data.pop("activity_ids", None)
        retro_payload = validated_data.pop("retro_input", None)

        post = super().update(instance, validated_data)

        if tag_objs is not None:
            post.tags.set(tag_objs)
        if act_objs is not None:
            post.activities.set(act_objs)

        # ✅ retro 갱신/생성/삭제
        if post.type == "retro":
            if retro_payload:
                if hasattr(post, "retro"):
                    for k, v in retro_payload.items():
                        setattr(post.retro, k, v)
                    post.retro.save()
                else:
                    Retro.objects.create(post=post, **retro_payload)
        else:
            # 타입이 retro가 아니면 레트로 레코드 제거(원치 않으면 주석)
            if hasattr(post, "retro"):
                post.retro.delete()

        return post
