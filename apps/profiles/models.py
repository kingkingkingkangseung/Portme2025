# apps/profiles/models.py
from django.db import models
from django.conf import settings

class JobRole(models.Model):
    """직무 마스터 (라디오/셀렉트용)"""
    GROUP_CHOICES = (
        ("dev", "개발"),
        ("design", "디자인"),
        ("pm", "기획/프로덕트"),
        ("biz", "비즈니스/경영"),
        ("etc", "기타"),
    )
    name  = models.CharField("직무명", max_length=100, unique=True)
    group = models.CharField("분야", max_length=16, choices=GROUP_CHOICES, default="dev")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["group", "order", "name"]

    def __str__(self):
        return f"[{self.get_group_display()}] {self.name}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    # 기존 필드(있으면 유지)
    display_name = models.CharField("표시 이름", max_length=50, blank=True)
    bio = models.TextField("소개", blank=True)
    avatar = models.ImageField("아바타", upload_to="avatars/", blank=True, null=True)
    website = models.URLField("웹사이트", blank=True)

    # ─ 사용자 카드(요구사항) ─
    full_name = models.CharField("이름", max_length=50, blank=True)
    github_linked = models.BooleanField("깃허브 연동 여부", default=False)

    class Level(models.TextChoices):
        STUDENT = "student", "학생"
        NEW     = "newgrad", "신입"
        EXP     = "experienced", "경력"
    level = models.CharField("레벨", max_length=12, choices=Level.choices, default=Level.STUDENT)

    job_role = models.ForeignKey(
        JobRole, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="직무"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Profile"
