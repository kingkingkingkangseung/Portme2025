from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Portfolio(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    concept_line = models.CharField("컨셉 라인", max_length=255)


    activities   = models.ManyToManyField(
        'activity.Activity',  # 앱 라벨이 'activity'라면
        blank=True,
        related_name='portfolios',
        verbose_name="활동 목록"
    )

    
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.concept_line[:20]} ({self.user.username})"