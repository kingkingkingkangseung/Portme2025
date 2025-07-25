from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass  # 지금은 필드 없어도 OK
