from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Portfolio(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField("포트폴리오 제목", max_length=200, blank=True, default="")
    selected_tags = models.JSONField("선택 태그", default=list, blank=True)
    work_style = models.TextField(
        "업무 스타일",
        blank=True,
        validators=[MaxLengthValidator(200)],
    )
    strengths = models.TextField(
        "강점",
        blank=True,
        validators=[MaxLengthValidator(200)],
    )
    concept_line = models.CharField("컨셉 라인", max_length=255, blank=True)


    activities   = models.ManyToManyField(
        'activity.Activity',  # 앱 라벨이 'activity'라면
        blank=True,
        related_name='portfolios',
        verbose_name="활동 목록"
    )

    
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        label = self.title or self.concept_line
        return f"{label[:20]} ({self.user.username})"


# ============================
# ERD 확장: 프로젝트/카테고리
# ============================

class ProjectCategory(models.Model):
    code = models.SlugField("코드", max_length=50, unique=True)
    name = models.CharField("카테고리명", max_length=100)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "code"]

    def __str__(self):
        return f"{self.name}({self.code})"


class Project(models.Model):
    """사용자별 프로젝트. ERD: project table"""
    class Position(models.TextChoices):
        LEADER = "leader", "팀장"
        MEMBER = "member", "팀원"
        INDIVIDUAL = "individual", "개인"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField("프로젝트명", max_length=200)
    period_start = models.DateField("시작일", null=True, blank=True)
    period_end = models.DateField("종료일", null=True, blank=True)
    category = models.ForeignKey(
        'portfolio.ProjectCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects'
    )
    position = models.CharField("직책", max_length=20, choices=Position.choices, default=Position.MEMBER)

    # ERD: activity와 1:M이지만, 기존 Activity 변경을 피하기 위해 M2M로 연결
    activities = models.ManyToManyField('activity.Activity', blank=True, related_name='projects')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-period_start"]

    def __str__(self):
        return f"{self.name} ({self.user.username})"
