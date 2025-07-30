# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from apps.user.views import (GoogleLoginImplicit, GoogleLoginCode, CustomLoginView, CustomRegisterView)

# 헬스체크용 뷰
def health(request):
    return HttpResponse("OK")

urlpatterns = [
    # 루트에 헬스체크 뷰 연결 (ELB가 “/”로 가져갑니다)
    path("", health, name="health-root"),
    # /health/ 로도 확인 가능
    path("health/", health, name="health"),

    # 기존 어드민/인증/API 엔드포인트
    path("admin/", admin.site.urls),

    # 1) Google Implicit Grant
    path(
        "api/auth/google/implicit/",
        GoogleLoginImplicit.as_view(),
        name="google_login_implicit"
    ),

    # 2) Google Authorization Code Grant
    path(
        "api/auth/google/code/",
        GoogleLoginCode.as_view(),
        name="google_login_code"
    ),

    # Custom login & registration (overrides rest-auth)
    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),

    # dj-rest-auth 기본 엔드포인트
    path("api/auth/", include("dj_rest_auth.urls")),

    # allauth social account
    path("api/social/", include("allauth.socialaccount.urls")),

    # Profile / Activity / Portfolio / Community APIs
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),
]
