from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 커뮤니티 필드
    bio = models.TextField(blank=True)
    # 로그인/소셜필드
    social_id = models.CharField(max_length=255, blank=True)
