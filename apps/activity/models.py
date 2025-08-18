from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivityCategory(models.Model):
    """활동 종류(경험의 종류) ex) 학업, 교내 활동, 공모전/대회 …"""
    key = models.SlugField(unique=True)                 # 'study', 'campus', 'contest' …
    name = models.CharField("이름", max_length=50)       # 표시용 한글명
    order = models.PositiveIntegerField(default=0)       # 정렬순서
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    class Kind(models.TextChoices):
        SOFT = "soft", "소프트"   # 협업/커뮤니케이션/리더십 등
        HARD = "hard", "하드"     # Python/Django/React/AWS 등

    name = models.CharField("태그 이름", max_length=50, unique=True)
    kind = models.CharField("속성", max_length=10, choices=Kind.choices, default=Kind.SOFT)

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")

    # ⬇️ 그림 기준 필드
    title        = models.CharField("활동명", max_length=200)
    period_start = models.DateField("활동 시작일", null=True, blank=True)
    period_end   = models.DateField("활동 종료일", null=True, blank=True)
    role         = models.CharField("역할 및 담당", max_length=200, blank=True)
    description  = models.TextField("활동 소개", blank=True)
    outcome      = models.TextField("성과", blank=True)
    attachment   = models.FileField("첨부파일", upload_to="activity_attachments/", blank=True, null=True)

    # ✅ 추가: 활동 종류 / 태그
    category = models.ForeignKey(
        ActivityCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="activities")

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)  # 편집 날짜

    class Meta:
        ordering = ["-updated_at", "-period_start"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class ActivityMemo(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="memos")
    content  = models.TextField("메모 내용")
    date     = models.DateField("날짜", auto_now_add=True)

    def __str__(self):
        return f"메모 #{self.pk} - {self.activity.title}"
