"""
Django settings for config project.
"""
import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv

# ───────────────────────────────
# 기본 설정
# ───────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "!!-DEV-ONLY-CHANGE-ME!!")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ───────────────────────────────
# 호스트 / CSRF
# ───────────────────────────────
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        "ALLOWED_HOSTS", "127.0.0.1,localhost,52.79.131.1"
    ).split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    "https://react-porters-grove.vercel.app",
    "https://grove.beer",
    "https://www.grove.beer",
    "http://52.79.131.1",
    "https://52.79.131.1",
]

# ───────────────────────────────
# INSTALLED_APPS
# ───────────────────────────────
SITE_ID = 1
INSTALLED_APPS = [
    # Django 기본
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # 외부 패키지
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "django_rest_passwordreset",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "corsheaders",

    # 내부 앱
    "apps.user",
    "apps.profiles",
    "apps.portfolio",
    "apps.activity",
    "apps.community",
    "apps.dashboard",
]

# ───────────────────────────────
# MIDDLEWARE
# ───────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # 반드시 CommonMiddleware보다 위
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ───────────────────────────────
# CORS 설정 (React <-> Django 통신 허용)
# ───────────────────────────────
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # 개발 중엔 True, 배포에선 아래 Origin만 허용
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://react-porters-grove.vercel.app",
]

# Explicitly allow methods/headers to ensure proxies/nginx don't block preflight
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
CORS_ALLOW_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-CSRFToken",
]

# ───────────────────────────────
# 템플릿
# ───────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# ───────────────────────────────
# 데이터베이스
# ───────────────────────────────
USE_MYSQL = bool(os.getenv("DB_HOST"))

if USE_MYSQL:
    import pymysql

    pymysql.install_as_MySQLdb()

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "portme_db"),
            "USER": os.getenv("DB_USER", "admin"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1;",
            },
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ───────────────────────────────
# 비밀번호 검증
# ───────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ───────────────────────────────
# 국제화
# ───────────────────────────────
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Seoul")
USE_I18N = True
USE_TZ = True

# ───────────────────────────────
# 정적 / 미디어 파일
# ───────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ───────────────────────────────
# 사용자 모델
# ───────────────────────────────
AUTH_USER_MODEL = "user.User"

# ───────────────────────────────
# 인증 / allauth 설정
# ───────────────────────────────
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# django-allauth 65 기준 설정
# - 이메일만으로 로그인
# - 회원가입 시 이메일/비밀번호만 필수
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = {
    "email": {"required": True},
    "password1": {"required": True},
    "password2": {"required": True},
}

# User 모델에는 username 필드가 있지만,
# 로그인/회원가입 시에는 사용하지 않도록 구성
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "none"

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# Email (SMTP) settings — read from .env
# If not set, use console backend in DEBUG; SMTP in production by default
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "noreply@example.com"
)
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "15"))

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ───────────────────────────────
# Google OAuth
# ───────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "https://react-porters-grove.vercel.app/google/callback/",
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL", "https://react-porters-grove.vercel.app"
)

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # "APP": {
        #     "client_id": GOOGLE_CLIENT_ID,
        #     "secret": GOOGLE_CLIENT_SECRET,
        #     "key": "",
        # },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

# ACCOUNT_ADAPTER = "apps.user.adapters.CustomAccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.user.adapters.CustomSocialAccountAdapter"

# ───────────────────────────────
# DRF / JWT
# ───────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

REST_AUTH = {"USE_JWT": True}
REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "apps.user.serializers.RegisterSerializer",
}

