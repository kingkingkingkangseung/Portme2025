from django.contrib import admin
from django.urls import path, include

from apps.user.views import (
    GoogleLoginImplicit,
    GoogleLoginCode,
    CustomLoginView,
    CustomRegisterView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Google OAuth2 로그인
    # 1) Implicit Grant
    path(
        'api/auth/google/implicit/',
        GoogleLoginImplicit.as_view(),
        name='google_login_implicit'
    ),
    # 2) Authorization Code Grant
    path(
        'api/auth/google/code/',
        GoogleLoginCode.as_view(),
        name='google_login_code'
    ),

    # ✅ 커스텀 로그인 / 회원가입
    path('api/auth/login/', CustomLoginView.as_view(), name='rest_login'),
    path('api/auth/registration/', CustomRegisterView.as_view(), name='rest_register'),

    # ✅ 기본 인증 라우트
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/social/', include('allauth.socialaccount.urls')),

    # ✅ 회원가입 기본 라우트 (allauth)
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),

    # ✅ 프로필 API
    path('api/profiles/', include('apps.profiles.urls')),

    # ✅ 활동 API
    path('api/activities/', include('apps.activity.urls')),

    # ✅ 포트폴리오 API
    path('api/portfolios/', include('apps.portfolio.urls')),

    # ✅ 커뮤니티 API
    path('api/community/', include('apps.community.urls')),
]
