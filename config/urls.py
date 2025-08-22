from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# user.views에서 필요한 뷰만 import
from apps.user.views import (
    GoogleLoginCode,
    GitHubLoginCode,
    CustomLoginView,
    CustomRegisterView,

)

# 헬스체크용 뷰
def health(request):
    return HttpResponse("OK")

def oauth_callback_echo(request):
    # http://localhost:8000/api/auth/github/callback/?code=XXXX 로 오면
    return HttpResponse(f"code = {request.GET.get('code')}")
    

urlpatterns = [
    # 헬스체크
    path("", health, name="health-root"),
    path("health/", health, name="health"),

    # 어드민
    path("admin/", admin.site.urls),

    # Google OAuth (Authorization Code)
    path(
        "api/auth/google/code/", GoogleLoginCode.as_view(), name="google_login_code"),

    #Github OAuth
    path("api/auth/github/code/", GitHubLoginCode.as_view(), name="github_login_code"),
    path("api/auth/github/callback/", oauth_callback_echo, name="github_callback_echo"),


    # Custom login & registration
    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),

    # dj-rest-auth 기본 엔드포인트
    path("api/auth/", include("dj_rest_auth.urls")),

    # 서비스 API
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),
]
