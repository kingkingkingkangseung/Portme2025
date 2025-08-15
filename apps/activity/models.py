from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")

    # ⬇️ 그림 기준 필드
    title        = models.CharField("활동명", max_length=200)
    period_start = models.DateField("활동 시작일", null=True, blank=True)
    period_end   = models.DateField("활동 종료일", null=True, blank=True)
    role         = models.CharField("역할 및 담당", max_length=200, blank=True)
    description  = models.TextField("활동 소개", blank=True)
    outcome      = models.TextField("성과", blank=True)
    attachment   = models.FileField("첨부파일", upload_to="activity_attachments/", blank=True, null=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)  # 편집 날짜

    class Meta:
        ordering = ["-updated_at", "-period_start"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class ActivityMemo(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="memos")
    content  = models.TextField("메모 내용")
    date     = models.DateField("날짜", auto_now_add=True)

    def __str__(self):
        return f"메모 #{self.pk} - {self.activity.title}"
