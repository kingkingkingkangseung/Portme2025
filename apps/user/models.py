from django.contrib.auth.models import AbstractUser
from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class User(AbstractUser):
    # 기존 필드 유지
    bio = models.TextField(blank=True)
    social_id = models.CharField(max_length=255, blank=True)

    # 👉 그림 기준 새 필드들 (전부 선택값)
    full_name = models.CharField("이름", max_length=50, blank=True)
    github_linked = models.BooleanField("깃허브 연동 여부", default=False)
    job_title = models.CharField("직무", max_length=100, blank=True)

    class Level(models.TextChoices):
        STUDENT = "student", "학생"
        JUNIOR  = "junior",  "신입"
        SENIOR  = "senior",  "경력"
    level = models.CharField("레벨", max_length=10, choices=Level.choices, blank=True)

    # 보유 스킬 (정규화)
    skills = models.ManyToManyField(Skill, blank=True, related_name="users")

    def __str__(self):
        return self.username or self.full_name or str(self.pk)
