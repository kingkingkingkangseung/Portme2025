from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.activity.models import Tag, Activity  # 🔹 활동앱의 태그/활동 재사용

User = get_user_model()

class Post(models.Model):
    TYPE_CHOICES = [
        ("article", "정보글"),
        ("question", "질문"),
        ("review",   "후기"),
        ("retro",    "회고록"),  # 🔹 추가
    ]
    VISIBILITY_CHOICES = [
        ("public",  "공개"),
        ("private", "비공개"),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default="article")

    # 회고록은 제목 없이도 쓸 수 있도록 blank 허용
    title       = models.CharField(max_length=200, blank=True)
    content     = models.TextField()

    # 선택: 기존 category 문자열 유지 (프론트에서 쓰면 계속 사용 가능)
    category    = models.CharField(max_length=50, blank=True)

    # 🔹 태그/활동/좋아요/스크랩
    tags        = models.ManyToManyField(Tag, blank=True, related_name="posts")
    activities  = models.ManyToManyField(Activity, blank=True, related_name="posts")
    likes       = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="liked_posts")
    scraps      = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="scrapped_posts")

    # 공개 범위(회고록에 주로 사용, 다른 타입도 선택 가능)
    visibility  = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public", blank=True)

    view_count  = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)  # = 편집 날짜

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return f"[{self.type}] {self.title or self.content[:20]}"

class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content    = models.TextField()
    is_answer  = models.BooleanField(default=False)   # 질문글에서 채택 여부 등에 활용 가능
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post_id}"
