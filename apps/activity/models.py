from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Activity(models.Model):
    user           = models.ForeignKey(User, on_delete=models.CASCADE)
    summary        = models.CharField("활동명", max_length=200)
    role           = models.CharField("역할", max_length=100)
    field          = models.CharField("분야", max_length=100)
    date           = models.DateField("활동 일자")
    skills         = models.JSONField("연관 스킬", default=list, blank=True)
    role_detail    = models.TextField("어떤 역할을 맡았나요?", blank=True)
    process_detail = models.TextField("과정 설명", blank=True)
    learn_detail   = models.TextField("무엇을 배웠나요?", blank=True)
    result_detail  = models.TextField("어떤 성과가 있었나요?", blank=True)
    thumbnail      = models.URLField("썸네일 URL", blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.summary} ({self.user.username})"