# apps/user/apps.py
from django.apps import AppConfig

class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.user"
    def ready(self):
        import apps.user.signals  # signals.py가 있다면 로딩
