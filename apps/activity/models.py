from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ActivityCategory(models.Model):
    """활동 종류(경험의 큰 분류)"""

    key = models.SlugField(unique=True)
    name = models.CharField("이름", max_length=50)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    class Kind(models.TextChoices):
        SOFT = "soft", "소프트 스킬"
        HARD = "hard", "하드 스킬"
        JOB = "job", "직무"

    name = models.CharField("태그 이름", max_length=50, unique=True)
    kind = models.CharField("구분", max_length=10, choices=Kind.choices, default=Kind.SOFT)

    def __str__(self) -> str:
        return f"{self.name} ({self.get_kind_display()})"


class Activity(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "진행 중"
        HIGHLIGHT = "highlight", "주요 스펙"
        COMPLETED = "completed", "완료"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")

    # 기본 정보
    title = models.CharField("활동명", max_length=200)
    period_start = models.DateField("활동 시작일", null=True, blank=True)
    period_end = models.DateField("활동 종료일", null=True, blank=True)
    role = models.CharField("역할 / 담당", max_length=200, blank=True)
    description = models.TextField("활동 소개", blank=True)
    outcome = models.TextField("성과", blank=True)
    attachment = models.FileField(
        "첨부 파일",
        upload_to="activity_attachments/",
        blank=True,
        null=True,
    )

    # 추가 정보
    subject = models.CharField("주제", max_length=200, blank=True)
    host = models.CharField("주최/주관", max_length=200, blank=True)
    work_title = models.CharField("출품작/프로젝트명", max_length=200, blank=True)
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

    # STAR 기록
    situation = models.TextField("상황(Situation)", blank=True)
    task_detail = models.TextField("과제(Task)", blank=True)
    action_detail = models.TextField("행동(Action)", blank=True)
    result_detail = models.TextField("결과(Result)", blank=True)
    takeaway = models.TextField("교훈(Takeaway)", blank=True)

    organization = models.CharField("소속 팀/회사", max_length=120, blank=True)
    plan_count = models.PositiveSmallIntegerField(default=0)
    design_count = models.PositiveSmallIntegerField(default=0)
    dev_count = models.PositiveSmallIntegerField(default=0)
    learned = models.TextField("배운 점", blank=True)
    link_url = models.URLField("링크 첨부", blank=True)

    category = models.ForeignKey(
        ActivityCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="activities")

    primary_tags = models.ManyToManyField("Tag", blank=True, related_name="primary_activities")
    secondary_tags = models.ManyToManyField("Tag", blank=True, related_name="secondary_activities")

    status = models.CharField(
        "보드 상태",
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )
    board_order = models.PositiveIntegerField("보드 정렬", default=0)
    is_deleted = models.BooleanField("휴지통 여부", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-period_start"]

    def __str__(self) -> str:
        return f"{self.title} ({self.user.username})"


class ActivityRole(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField("역할명", max_length=50)
    count = models.PositiveSmallIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.activity.title} - {self.name} x{self.count}"


class ActivityMemo(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="memos")
    content = models.TextField("메모 내용")
    date = models.DateField("날짜", auto_now_add=True)

    def __str__(self) -> str:
        return f"메모 #{self.pk} - {self.activity.title}"


# =========================
# 스펙: 경력 / 수상 / 자격 / 해외경험 / 외국어
# =========================


class Career(models.Model):
    """경력 스펙"""

    class EmploymentType(models.TextChoices):
        REGULAR = "regular", "정규직"
        CONTRACT = "contract", "계약직"
        INTERN = "intern", "인턴"
        FREELANCER = "freelancer", "프리랜서"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="careers")
    company_name = models.CharField("회사명", max_length=200)
    employment_type = models.CharField(
        "재직 형태",
        max_length=20,
        choices=EmploymentType.choices,
        blank=True,
    )
    position = models.CharField("직무/부서", max_length=200, blank=True)
    period_start = models.DateField("시작일", null=True, blank=True)
    period_end = models.DateField("종료일", null=True, blank=True)
    is_current = models.BooleanField("재직 중", default=False)

    situation = models.TextField("상황(Situation)", blank=True)
    task_detail = models.TextField("과제(Task)", blank=True)
    action_detail = models.TextField("행동(Action)", blank=True)
    result_detail = models.TextField("결과(Result)", blank=True)

    attachment = models.FileField(
        "첨부 파일",
        upload_to="career_attachments/",
        blank=True,
        null=True,
    )
    link_url = models.URLField("링크 추가", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-period_start"]

    def __str__(self) -> str:
        return f"{self.company_name} ({self.user.username})"


class Award(models.Model):
    """수상 스펙"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="awards")
    awards_name = models.CharField("공모전·대회명", max_length=200)
    awards_grade = models.CharField("수상 내역", max_length=100, blank=True)
    achievement_date = models.DateField("수상일")
    issuer = models.CharField("주관·수여 기관", max_length=200, blank=True)
    description = models.TextField("설명", blank=True)
    attachment = models.FileField(
        "첨부 파일",
        upload_to="award_attachments/",
        blank=True,
        null=True,
    )
    link_url = models.URLField("링크 추가", blank=True)

    def __str__(self) -> str:
        return f"{self.awards_name} ({self.user.username})"


class Certification(models.Model):
    """자격증 스펙"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certifications")
    c_name = models.CharField("자격증명", max_length=200)
    achievement_date = models.DateField("취득일")
    expiration_date = models.DateField("만료일", null=True, blank=True)
    issuer = models.CharField("발급 기관", max_length=200, blank=True)
    description = models.TextField("설명", blank=True)
    attachment = models.FileField(
        "첨부 파일",
        upload_to="certification_attachments/",
        blank=True,
        null=True,
    )
    link_url = models.URLField("링크 추가", blank=True)

    def __str__(self) -> str:
        return f"{self.c_name} ({self.user.username})"


class GlobalExp(models.Model):
    """해외 경험"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="global_exps")
    g_category = models.CharField("경험 카테고리", max_length=100)  # 교환학생, 어학연수 등
    nation = models.CharField("국가", max_length=100)
    period_start = models.DateField("시작일", null=True, blank=True)
    period_end = models.DateField("종료일", null=True, blank=True)
    is_current = models.BooleanField("진행 중", default=False)
    language = models.CharField("사용 언어", max_length=100, blank=True)
    attachment = models.FileField(
        "첨부 파일",
        upload_to="globalexp_attachments/",
        blank=True,
        null=True,
    )
    link_url = models.URLField("링크 추가", blank=True)
    description = models.TextField("설명", blank=True)

    def __str__(self) -> str:
        return f"{self.g_category} in {self.nation} ({self.user.username})"


class ForeignLang(models.Model):
    """외국어 능력 / 스펙"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="foreign_langs")
    lang_name = models.CharField("언어", max_length=100)

    class Proficiency(models.TextChoices):
        DAILY = "daily", "일상 회화"
        BUSINESS = "business", "비즈니스 회화"
        NATIVE = "native", "원어민 수준"

    lang_level = models.CharField(
        "구사 수준",
        max_length=20,
        choices=Proficiency.choices,
        blank=True,
    )

    exam_name = models.CharField("시험명", max_length=100, blank=True)
    exam_grade = models.CharField("점수/등급", max_length=100, blank=True)
    achievement_date = models.DateField("취득일", null=True, blank=True)

    attachment = models.FileField(
        "첨부 파일",
        upload_to="foreignlang_attachments/",
        blank=True,
        null=True,
    )
    link_url = models.URLField("링크 추가", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.lang_name} ({self.user.username})"


# ============================
# ERD 확장: Activity 와 Skill 매핑(레벨)
# ============================


class ActivityHardSkill(models.Model):
    activity = models.ForeignKey("activity.Activity", on_delete=models.CASCADE, related_name="hard_skill_links")
    hard_skill = models.ForeignKey("profiles.HardSkill", on_delete=models.CASCADE, related_name="activity_links")
    level = models.PositiveSmallIntegerField(default=1)
    level_description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("activity", "hard_skill")

    def __str__(self) -> str:
        return f"{self.activity_id} - {self.hard_skill} (L{self.level})"


class ActivitySoftSkill(models.Model):
    activity = models.ForeignKey("activity.Activity", on_delete=models.CASCADE, related_name="soft_skill_links")
    soft_skill = models.ForeignKey("profiles.SoftSkill", on_delete=models.CASCADE, related_name="activity_links")
    level = models.PositiveSmallIntegerField(default=1)
    level_description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("activity", "soft_skill")

    def __str__(self) -> str:
        return f"{self.activity_id} - {self.soft_skill} (L{self.level})"


# ============================
# 세부 활동(보조 활동)
# ============================


class SubActivity(models.Model):
    """
    하나의 Activity 아래에 포함되는 세부 활동 카드.
    예) 사용자 리서치, 시나리오 기획, 프로토타입 제작 등
    """

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="sub_activities",
    )

    # 기본 정보
    title = models.CharField("활동명", max_length=200)
    summary = models.CharField("요약", max_length=255, blank=True)

    period_start = models.DateField("시작일", null=True, blank=True)
    period_end = models.DateField("종료일", null=True, blank=True)
    is_ongoing = models.BooleanField("진행 중 여부", default=False)

    metric = models.CharField("성과 지표", max_length=255, blank=True)
    hard_tools = models.CharField("툴/기술 스택", max_length=255, blank=True)
    soft_skills = models.CharField("소프트 스킬", max_length=255, blank=True)

    # STAR 상세
    situation = models.TextField("상황", blank=True)
    task_detail = models.TextField("과제", blank=True)
    action_detail = models.TextField("행동", blank=True)
    result_detail = models.TextField("결과", blank=True)
    takeaway = models.TextField("교훈", blank=True)

    attachment = models.FileField(
        "첨부 파일",
        upload_to="subactivity_attachments/",
        blank=True,
        null=True,
    )
    link_url = models.URLField("관련 링크", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["period_start", "id"]

    def __str__(self) -> str:
        return f"{self.activity_id} - {self.title}"

