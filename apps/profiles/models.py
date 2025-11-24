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
    """사용자 프로필 + 포트폴리오 상단 카드 정보."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

<<<<<<< HEAD
    # 기본 프로필 정보
    display_name = models.CharField("표시 이름", max_length=50, blank=True)
=======
    full_name = models.CharField("이름", max_length=50, blank=True)
>>>>>>> eabf36c ( migrations 수정)
    bio = models.TextField("소개", blank=True)
    avatar = models.ImageField("아바타", upload_to="avatars/", blank=True, null=True)

<<<<<<< HEAD
    # 사용자 카드(요약 영역)
    full_name = models.CharField("이름", max_length=50, blank=True)
    github_linked = models.BooleanField("깃허브 연동 여부", default=False)

    class Level(models.TextChoices):
        STUDENT = "student", "학생"
        NEW = "newgrad", "신입"
        EXP = "experienced", "경력"

    level = models.CharField(
        "레벨",
        max_length=12,
        choices=Level.choices,
        default=Level.STUDENT,
    )

    # 추가 입력 필드
    birth_date = models.DateField("생년월일", null=True, blank=True)
    phone_number = models.CharField("전화번호", max_length=20, blank=True)
    email = models.EmailField("이메일", blank=True)
=======
    birth_date = models.DateField("생년월일", null=True, blank=True)
    phone_number = models.CharField("전화번호", max_length=20, blank=True)
    contact_email = models.EmailField("연락 이메일", blank=True)

    school_name = models.CharField("학교명", max_length=120, blank=True)
    admission_date = models.DateField("입학 연월", null=True, blank=True)
    graduation_date = models.DateField("졸업 연월", null=True, blank=True)
>>>>>>> eabf36c ( migrations 수정)

    job_role = models.ForeignKey(
        JobRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="직무",
    )

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


class ProfileLink(models.Model):
    """프로필 카드에서 사용하는 외부 링크들(대표 링크/추가 링크)."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="links",
    )
    title = models.CharField("링크명", max_length=100, blank=True)
    url = models.URLField("URL")
    order = models.PositiveIntegerField("순서", default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.profile_id} - {self.title or self.url}"


class Education(models.Model):
    """학력 정보: 학교구분/재학기간/전공/학점 등."""

    class SchoolType(models.TextChoices):
        HIGH = "HIGH", "고등학교"
        UNIV_2_3 = "UNIV_2_3", "대학교(2,3년)"
        UNIV_4 = "UNIV_4", "대학교(4년)"
        GRAD_MS = "GRAD_MS", "대학원(석사)"
        GRAD_PHD = "GRAD_PHD", "대학원(박사)"

    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", "재학중"
        GRADUATED = "GRADUATED", "졸업"
        COMPLETED = "COMPLETED", "수료"
        EXPECTED = "EXPECTED", "졸업예정"
        DROPPED = "DROPPED", "중퇴"
        LEAVE = "LEAVE", "휴학"
        WITHDRAWN = "WITHDRAWN", "자퇴"

    class MajorType(models.TextChoices):
        MAJOR = "MAJOR", "주전공"
        MINOR = "MINOR", "부전공"
        DOUBLE = "DOUBLE", "이중전공"
        SECOND = "SECOND", "복수전공"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="educations",
    )

    school_type = models.CharField("학교구분", max_length=20, choices=SchoolType.choices)
    school_name = models.CharField("학교명", max_length=100)
    is_transfer = models.BooleanField("편입 여부", default=False)

    # YYYY.MM 포맷으로 저장
    start_year_month = models.CharField("입학연월", max_length=7, blank=True)
    end_year_month = models.CharField("졸업연월", max_length=7, blank=True)
    status = models.CharField(
        "졸업 여부",
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
    )

    # 전공 관련
    major_type = models.CharField(
        "전공구분",
        max_length=20,
        choices=MajorType.choices,
        blank=True,
    )
    major_name = models.CharField("전공명", max_length=100, blank=True)

    # 학점/총점
    gpa = models.DecimalField(
        "학점",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )
    gpa_scale = models.DecimalField(
        "총점",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover - display only
        return f"{self.profile_id} - {self.school_name}"

