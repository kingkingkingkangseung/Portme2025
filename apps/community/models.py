from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    TYPE_CHOICES = [
        ("article", "정보글"),
        ("question", "질문"),
        ("review", "후기"),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default="article")
    title       = models.CharField(max_length=200)
    content     = models.TextField()
    category    = models.CharField(max_length=50, blank=True)
    tags        = models.JSONField(default=list, blank=True)
    like_count  = models.PositiveIntegerField(default=0)
    view_count  = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.type})"


class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content    = models.TextField()
    is_answer  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.post_id}"
