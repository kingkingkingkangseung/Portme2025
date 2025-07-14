from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    birthdate = models.DateField(null=True, blank=True)

    certifications = models.TextField(blank=True)  # 예: '정보처리기사,SQLD,GA4'
    skills = models.TextField(blank=True)          # 예: 'Notion,Figma,MySQL'

    contact_info = models.CharField(max_length=255, blank=True)
    desired_job = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Profile"
