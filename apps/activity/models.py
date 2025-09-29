from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ===== Activity 관련 =====
class ActivityCategory(models.Model):
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
        SOFT = "soft", "소프트"
        HARD = "hard", "하드"
        JOB = "job", "직무"

    name = models.CharField("태그 이름", max_length=50, unique=True)
    kind = models.CharField("속성", max_length=10, choices=Kind.choices, default=Kind.SOFT)

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    title = models.CharField("활동명", max_length=200)
    period_start = models.DateField("활동 시작일", null=True, blank=True)
    period_end = models.DateField("활동 종료일", null=True, blank=True)
    role = models.CharField("역할 및 담당", max_length=200, blank=True)
    description = models.TextField("활동 소개", blank=True)
    outcome = models.TextField("성과", blank=True)
    attachment = models.FileField(upload_to="activity_attachments/", blank=True, null=True)

    organization = models.CharField("소속 팀/회사", max_length=120, blank=True)
    plan_count = models.PositiveSmallIntegerField(default=0)
    design_count = models.PositiveSmallIntegerField(default=0)
    dev_count = models.PositiveSmallIntegerField(default=0)
    learned = models.TextField("배운 점", blank=True)
    link_url = models.URLField("링크 첨부", blank=True)

    category = models.ForeignKey(
        ActivityCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities"
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="activities")
    primary_tags = models.ManyToManyField("Tag", blank=True, related_name="primary_activities")
    secondary_tags = models.ManyToManyField("Tag", blank=True, related_name="secondary_activities")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-period_start"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class ActivityRole(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField("역할명", max_length=50)
    count = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.activity.title} - {self.name} x{self.count}"


class ActivityMemo(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="memos")
    content = models.TextField("메모 내용")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"메모 #{self.pk} - {self.activity.title}"


# ===== Award / Certification =====
class Award(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="awards")
    awards_name = models.CharField("수상명", max_length=200)
    awards_grade = models.CharField("등급/수상내역", max_length=100, blank=True)
    achievement_date = models.DateField("수상일자")
    description = models.TextField("설명", blank=True)
    attachment = models.FileField(upload_to="award_attachments/", blank=True, null=True)

    def __str__(self):
        return f"{self.awards_name} ({self.user.username})"


class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certifications")
    c_name = models.CharField("자격증명", max_length=200)
    achievement_date = models.DateField("취득일자")
    expiration_date = models.DateField("만료일자", null=True, blank=True)
    issuer = models.CharField("발급기관", max_length=200, blank=True)
    description = models.TextField("설명", blank=True)
    attachment = models.FileField(upload_to="certification_attachments/", blank=True, null=True)

    def __str__(self):
        return f"{self.c_name} ({self.user.username})"


# ===== GlobalExp =====
class GlobalExp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="global_exps")
    g_category = models.CharField("해외경험 구분", max_length=30)  # 프론트에서 선택 (교환학생, 어학연수 등)
    nation = models.CharField("국가", max_length=100)
    start_date = models.DateField("시작일")
    end_date = models.DateField("종료일", null=True, blank=True)
    language = models.CharField("사용 언어", max_length=100, blank=True)
    attachment = models.FileField(upload_to="globalexp_attachments/", blank=True, null=True)
    description = models.TextField("설명", blank=True)

    def __str__(self):
        return f"{self.g_category} - {self.nation} ({self.user.username})"


# ===== ForeignLang =====
class ForeignLang(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="foreign_langs")
    lang_name = models.CharField("언어명", max_length=50)
    lang_level = models.CharField("숙련도", max_length=50, blank=True)
    achievement_date = models.DateField("취득일자", null=True, blank=True)
    attachment = models.FileField(upload_to="foreignlang_attachments/", blank=True, null=True)

    def __str__(self):
        return f"{self.lang_name} ({self.user.username})"
