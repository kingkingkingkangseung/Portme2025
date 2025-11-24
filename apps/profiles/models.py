# apps/profiles/models.py
from django.db import models
from django.conf import settings


class JobRole(models.Model):
    """직무 마스터 (직무/그룹 관리)."""

    GROUP_CHOICES = (
        ("dev", "개발"),
        ("design", "디자인"),
        ("pm", "기획/프로덕트"),
        ("biz", "비즈니스/경영"),
        ("etc", "기타"),
    )

    name = models.CharField("직무명", max_length=100, unique=True)
    group = models.CharField("분야", max_length=16, choices=GROUP_CHOICES, default="dev")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # ERD 확장: 상위 직무 카테고리 (j_category)
    job_category = models.ForeignKey(
        "profiles.JobCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="job_roles",
        verbose_name="직무 카테고리",
    )

    class Meta:
        ordering = ["group", "order", "name"]

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"[{self.get_group_display()}] {self.name}"


class Profile(models.Model):
    class GraduationStatus(models.TextChoices):
        ENROLLED = "재학중", "재학중"
        GRADUATED = "졸업", "졸업"
        COMPLETED = "수료", "수료"
        EXPECTED = "졸업예정", "졸업예정"
        STOPPED = "중퇴", "중퇴"
        LEAVE = "휴학", "휴학"
        WITHDRAWN = "자퇴", "자퇴"

    """사용자 프로필 + 포트폴리오 상단 카드 정보."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    full_name = models.CharField("이름", max_length=50, blank=True)
    bio = models.TextField("소개", blank=True)
    avatar = models.ImageField("아바타", upload_to="avatars/", blank=True, null=True)

    birth_date = models.DateField("생년월일", null=True, blank=True)
    phone_number = models.CharField("전화번호", max_length=20, blank=True)
    contact_email = models.EmailField("연락 이메일", blank=True)

    school_name = models.CharField("학교명", max_length=120, blank=True)
    admission_date = models.DateField("입학 연월", null=True, blank=True)
    graduation_date = models.DateField("졸업 연월", null=True, blank=True)
    graduation_status = models.CharField(
        "졸업 여부",
        max_length=30,
        blank=True,
        choices=GraduationStatus.choices,
    )
    gpa = models.CharField("학점", max_length=20, blank=True, null=True)
    gpa_total = models.CharField("총점", max_length=20, blank=True, null=True)

    job_role = models.ForeignKey(
        JobRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="직무",
    )
    job_role_name = models.CharField("직무명(직접 입력)", max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.user.username} - Profile"


class ProfileLink(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="links"
    )
    label = models.CharField("링크 이름", max_length=50, blank=True)
    url = models.URLField("URL")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        base = self.label or self.url
        return f"{self.profile_id} - {base}"


class ProfileMajor(models.Model):
    class MajorType(models.TextChoices):
        MAJOR = "major", "주전공"
        DOUBLE = "double", "복수전공"
        MINOR = "minor", "부전공"
        OTHER = "other", "기타"

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="majors")
    major_type = models.CharField("전공 구분", max_length=20, choices=MajorType.choices, blank=True)
    major_name = models.CharField("전공명", max_length=120)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.profile_id} - {self.major_name}"


# ============================
# ERD 확장: 직무/스킬 구조화
# ============================


class JobCategory(models.Model):
    name = models.CharField("카테고리명", max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:  # pragma: no cover - display only
        return self.name


class HardSkill(models.Model):
    name = models.CharField("하드스킬명", max_length=100, unique=True)
    code = models.SlugField("스킬코드", max_length=64, unique=True)

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.name} ({self.code})"


class SoftSkill(models.Model):
    name = models.CharField("소프트스킬명", max_length=100, unique=True)

    def __str__(self) -> str:  # pragma: no cover - display only
        return self.name


class JobHardSkill(models.Model):
    job_role = models.ForeignKey("profiles.JobRole", on_delete=models.CASCADE)
    hard_skill = models.ForeignKey("profiles.HardSkill", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("job_role", "hard_skill")

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.job_role} - {self.hard_skill}"


class JobSoftSkill(models.Model):
    job_role = models.ForeignKey("profiles.JobRole", on_delete=models.CASCADE)
    soft_skill = models.ForeignKey("profiles.SoftSkill", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("job_role", "soft_skill")

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.job_role} - {self.soft_skill}"
