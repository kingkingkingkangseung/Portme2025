from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ActivityCategory(models.Model):
    """활동 종류(경험의 종류) ex) 학업, 교내 활동, 공모전/대회 …"""
    key = models.SlugField(unique=True)
    name = models.CharField("이름", max_length=50)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    class Kind(models.TextChoices):
        SOFT = "soft", "소프트"   # 협업/커뮤니케이션/리더십 등
        HARD = "hard", "하드"     # Python/Django/React/AWS 등
        JOB  = "job",  "직무"     # 기획/디자인/PM 등

    name = models.CharField("태그 이름", max_length=50, unique=True)
    kind = models.CharField("속성", max_length=10, choices=Kind.choices, default=Kind.SOFT)

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")

    # 기존 필드
    title        = models.CharField("활동명", max_length=200)
    period_start = models.DateField("활동 시작일", null=True, blank=True)
    period_end   = models.DateField("활동 종료일", null=True, blank=True)
    role         = models.CharField("역할 및 담당", max_length=200, blank=True)
    description  = models.TextField("활동 소개", blank=True)
    outcome      = models.TextField("성과", blank=True)
    attachment   = models.FileField("첨부파일", upload_to="activity_attachments/", blank=True, null=True)

    # ✅ 추가: 소속/팀/회사
    organization = models.CharField("소속 팀/회사", max_length=120, blank=True)

    # ✅ 추가: 팀 구성 요약(숫자)
    plan_count   = models.PositiveSmallIntegerField(default=0)
    design_count = models.PositiveSmallIntegerField(default=0)
    dev_count    = models.PositiveSmallIntegerField(default=0)

    # ✅ 추가: 배운 점
    learned      = models.TextField("배운 점", blank=True)

    # ✅ 추가: 링크 첨부(파일 1개 + 링크 1개를 UI에서 받는 형태)
    link_url     = models.URLField("링크 첨부", blank=True)

    # 그대로 유지: 카테고리 / 태그(M2M)
    category = models.ForeignKey(
        "ActivityCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="activities"
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="activities")  # 기존 유지

    # ✅ 추가: UI용 주요/보조 태그 (Tag 모델 그대로 사용)
    primary_tags   = models.ManyToManyField("Tag", blank=True, related_name="primary_activities")
    secondary_tags = models.ManyToManyField("Tag", blank=True, related_name="secondary_activities")

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-period_start"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"


# ✅ 추가: 자유 입력 역할(“직접 입력하여 역할 추가하기”)
class ActivityRole(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField("역할명", max_length=50)
    count = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.activity.title} - {self.name} x{self.count}"


class ActivityMemo(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="memos")
    content  = models.TextField("메모 내용")
    date     = models.DateField("날짜", auto_now_add=True)

    def __str__(self):
        return f"메모 #{self.pk} - {self.activity.title}"