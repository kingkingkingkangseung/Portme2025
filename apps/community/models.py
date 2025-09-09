# apps/community/models.py (파일 경로는 현재 모델 파일 기준)
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.activity.models import Tag, Activity

User = get_user_model()

class Post(models.Model):
    TYPE_CHOICES = [
        ("article", "정보글"),
        ("question", "질문"),
        ("review",   "후기"),
        ("retro",    "회고록"),
    ]
    VISIBILITY_CHOICES = [
        ("public",  "공개"),
        ("private", "비공개"),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default="article")

    # 회고는 제목 없이도 가능
    title       = models.CharField(max_length=200, blank=True)

    # ✅ 회고 폼에 본문 입력이 없을 수 있으므로 blank 허용
    content     = models.TextField(blank=True)

    category    = models.CharField(max_length=50, blank=True)

    tags        = models.ManyToManyField(Tag, blank=True, related_name="posts")
    activities  = models.ManyToManyField(Activity, blank=True, related_name="posts")
    likes       = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="liked_posts")
    scraps      = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="scrapped_posts")

    visibility  = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public", blank=True)

    view_count  = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return f"[{self.type}] {self.title or (self.content[:20] if self.content else '')}"


# ✅ 회고 상세(서브테이블): 기존 Post에 영향 최소화
class Retro(models.Model):
    TYPE_CHOICES = [
        ("KPT", "Keep-Problem-Try"),
        ("AAR", "After Action Review"),
    ]
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="retro")

    retro_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # 공통 메타
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(default=0)   # 시간/분 합산
    mood = models.PositiveSmallIntegerField(default=3)          # 1~5 등급 가정

    # KPT
    keep = models.TextField(null=True, blank=True)
    problem = models.TextField(null=True, blank=True)
    try_field = models.TextField(null=True, blank=True)

    # AAR
    objective = models.TextField(null=True, blank=True)
    fact = models.TextField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.retro_type} for Post#{self.post_id}"


class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content    = models.TextField()
    is_answer  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post_id}"
