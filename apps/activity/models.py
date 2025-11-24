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
        SOFT = "soft", "소프트"
        HARD = "hard", "하드"
        JOB  = "job",  "직무"

    name = models.CharField("태그 이름", max_length=50, unique=True)
    kind = models.CharField("속성", max_length=10, choices=Kind.choices, default=Kind.SOFT)

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"


class Activity(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "진행 중"
        HIGHLIGHT = "highlight", "주요 스펙"
        COMPLETED = "completed", "완료"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")

    # 기본 정보
    title        = models.CharField("활동명", max_length=200)
    period_start = models.DateField("활동 시작일", null=True, blank=True)
    period_end   = models.DateField("활동 종료일", null=True, blank=True)
    role         = models.CharField("역할 및 담당", max_length=200, blank=True)
    description  = models.TextField("활동 소개", blank=True)
    outcome      = models.TextField("성과", blank=True)
    attachment   = models.FileField("첨부파일", upload_to="activity_attachments/", blank=True, null=True)

    # 추가
    subject      = models.CharField("주제", max_length=200, blank=True)
    host         = models.CharField("주최/주관", max_length=200, blank=True)
    work_title   = models.CharField("출품작/프로젝트명", max_length=200, blank=True)
    participation_type = models.CharField(
        "참여 형태",
        max_length=20,
        choices=(
            ("team", "팀"),
            ("individual", "개인"),
        ),
        blank=True,
    )
    is_awarded = models.BooleanField("수상 여부", default=False)
    award_detail = models.CharField("수상 내역", max_length=200, blank=True)

    situation = models.TextField("상황(Situation)", blank=True)
    task_detail = models.TextField("과제(Task)", blank=True)
    action_detail = models.TextField("행동(Action)", blank=True)
    result_detail = models.TextField("결과(Result)", blank=True)
    takeaway= models.TextField("교훈(Takeaway)", blank=True)
    
    organization = models.CharField("소속 팀/회사", max_length=120, blank=True)
    plan_count   = models.PositiveSmallIntegerField(default=0)
    design_count = models.PositiveSmallIntegerField(default=0)
    dev_count    = models.PositiveSmallIntegerField(default=0)
    learned      = models.TextField("배운 점", blank=True)
    link_url     = models.URLField("링크 첨부", blank=True)

    category = models.ForeignKey(
        ActivityCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities"
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="activities")

    primary_tags   = models.ManyToManyField("Tag", blank=True, related_name="primary_activities")
    secondary_tags = models.ManyToManyField("Tag", blank=True, related_name="secondary_activities")

    status = models.CharField(
        "보드 상태",
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    board_order = models.PositiveIntegerField("보드 정렬", default=0)
    is_deleted = models.BooleanField("삭제 여부", default=False)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

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
    content  = models.TextField("메모 내용")
    date     = models.DateField("날짜", auto_now_add=True)

    def __str__(self):
        return f"메모 #{self.pk} - {self.activity.title}"


# =========================
# 📌 새로운 모델들
# =========================
class Award(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="awards")
    awards_name = models.CharField("수상명", max_length=200)
    awards_grade = models.CharField("등급/수상내역", max_length=100, blank=True)
    achievement_date = models.DateField("수상일자")
    description = models.TextField("설명", blank=True)
    attachment = models.FileField("첨부파일", upload_to="award_attachments/", blank=True, null=True)

    def __str__(self):
        return f"{self.awards_name} ({self.user.username})"


class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certifications")
    c_name = models.CharField("자격증명", max_length=200)
    achievement_date = models.DateField("취득일자")
    expiration_date = models.DateField("만료일자", null=True, blank=True)
    issuer = models.CharField("발급기관", max_length=200, blank=True)
    description = models.TextField("설명", blank=True)
    attachment = models.FileField("첨부파일", upload_to="certification_attachments/", blank=True, null=True)

    def __str__(self):
        return f"{self.c_name} ({self.user.username})"


class GlobalExp(models.Model):
    """해외 경험"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="global_exps")
    g_category = models.CharField("경험 카테고리", max_length=100)  # 교환학생, 어학연수 등
    nation = models.CharField("국가", max_length=100)
    period_start = models.DateField("시작일", null=True, blank=True)
    period_end = models.DateField("종료일", null=True, blank=True)
    language = models.CharField("사용 언어", max_length=100, blank=True)
    attachment = models.FileField("첨부파일", upload_to="globalexp_attachments/", blank=True, null=True)
    description = models.TextField("설명", blank=True)

    def __str__(self):
        return f"{self.g_category} in {self.nation} ({self.user.username})"


class ForeignLang(models.Model):
    """외국어 능력"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="foreign_langs")
    lang_name = models.CharField("언어명", max_length=100)
    lang_level = models.CharField("수준", max_length=50)  # 초급, 중급, 고급
    achievement_date = models.DateField("취득일자", null=True, blank=True)
    attachment = models.FileField("첨부파일", upload_to="foreignlang_attachments/", blank=True, null=True)

    def __str__(self):
        return f"{self.lang_name} ({self.user.username})"


# ============================
# ERD 확장: Activity ↔ Skill 매핑(레벨)
# ============================

class ActivityHardSkill(models.Model):
    activity = models.ForeignKey('activity.Activity', on_delete=models.CASCADE, related_name='hard_skill_links')
    hard_skill = models.ForeignKey('profiles.HardSkill', on_delete=models.CASCADE, related_name='activity_links')
    level = models.PositiveSmallIntegerField(default=1)
    level_description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("activity", "hard_skill")

    def __str__(self):
        return f"{self.activity_id} - {self.hard_skill} (L{self.level})"


class ActivitySoftSkill(models.Model):
    activity = models.ForeignKey('activity.Activity', on_delete=models.CASCADE, related_name='soft_skill_links')
    soft_skill = models.ForeignKey('profiles.SoftSkill', on_delete=models.CASCADE, related_name='activity_links')
    level = models.PositiveSmallIntegerField(default=1)
    level_description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("activity", "soft_skill")

    def __str__(self):
        return f"{self.activity_id} - {self.soft_skill} (L{self.level})"
