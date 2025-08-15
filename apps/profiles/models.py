from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    display_name = models.CharField("표시 이름", max_length=50, blank=True)
    bio = models.TextField("소개", blank=True)
    avatar = models.ImageField("아바타", upload_to="avatars/", blank=True, null=True)
    website = models.URLField("웹사이트", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Profile"
