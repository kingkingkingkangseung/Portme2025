from django.conf import settings
from django.db import models


class ExperienceNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="experience_notes",
    )
    date = models.DateField("메모 날짜")
    content = models.TextField("메모 내용", blank=True)
    activity = models.ForeignKey(
        "activity.Activity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="experience_notes",
    )
    project = models.ForeignKey(
        "portfolio.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="experience_notes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date", "-updated_at"]

    def __str__(self):
        return f"{self.user} @ {self.date}"
