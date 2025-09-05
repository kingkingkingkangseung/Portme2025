"""
Django settings for config project.
"""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ── ENV 로드 ──
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── 보안/디버그 ──
SECRET_KEY = os.getenv("SECRET_KEY", "!!-DEV-ONLY-CHANGE-ME!!")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ── 호스트/CSRF ──
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()
]
CSRF_TRUSTED_ORIGINS = []
for h in ALLOWED_HOSTS:
    if h not in ("localhost", "127.0.0.1"):
        CSRF_TRUSTED_ORIGINS += [f"http://{h}", f"https://{h}"]

# ====================
# Application definition
# ====================
SITE_ID = 1
INSTALLED_APPS = [
    # Django
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'django.contrib.sites',

    # DRF + Auth
    'rest_framework', 'rest_framework.authtoken',
    'dj_rest_auth', 'dj_rest_auth.registration',

    # allauth
    'allauth', 'allauth.account', 'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',

    # Apps
    'apps.user', 'apps.profiles', 'apps.portfolio', 'apps.activity', 'apps.community',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# ====================
# Database (RDS ↔ SQLite 자동 전환)
# ====================
USE_MYSQL = bool(os.getenv("DB_HOST"))  # .env에 DB_HOST 있으면 MySQL 사용

if USE_MYSQL:
    import pymysql  # type: ignore
    pymysql.install_as_MySQLdb()

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'portme_db'),
            'USER': os.getenv('DB_USER', 'admin'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1;",
            },
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}
    }

# ====================
# Password Validation
# ====================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ====================
# I18N
# ====================
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Seoul")
USE_I18N = True
USE_TZ = True

# ====================
# Static / Media
# ====================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ====================
# User Model
# ====================
AUTH_USER_MODEL = 'user.User'

# ====================
# Auth Backends
# ====================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ====================
# allauth
# ====================
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
DEFAULT_FROM_EMAIL = 'noreply@example.com'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv("GOOGLE_CLIENT_ID"),
            'secret': os.getenv("GOOGLE_CLIENT_SECRET"),
            'key': ''
        },
        "SCOPE": ["openid", "email", "profile"],
        "AUTH_PARAMS": {
            "access_type": "offline",
            "prompt": "consent"
        },
        "OAUTH_PKCE_ENABLED": True,
        "REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI"),
    },

    'github': {
        'APP': {
            'client_id': os.getenv("GITHUB_CLIENT_ID"),
            'secret': os.getenv("GITHUB_CLIENT_SECRET"),
            'key': ''
        },
        "SCOPE": ["read:user", "user:email"],
        "REDIRECT_URI": os.getenv("GITHUB_REDIRECT_URI"),
    }
}

ACCOUNT_ADAPTER = 'apps.user.adapters.CustomAccountAdapter'

# ====================
# DRF / JWT
# ====================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
REST_AUTH = {'USE_JWT': True}
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'apps.user.serializers.RegisterSerializer'
}
