from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.http import JsonResponse

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

def google_callback_echo(request):
    """
    GET /api/auth/google/callback/?code=... 를 받아 code를 그대로 보여주는 디버그용 뷰
    """
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"detail": "code not found"}, status=400)
    # 필요 시 state도 확인 가능
    state = request.GET.get("state")
    return JsonResponse({"code": code, "state": state}, status=200)

def oauth_callback_echo(request):
    # http://localhost:8000/api/auth/github/callback/?code=XXXX 로 오면
    return HttpResponse(f"code = {request.GET.get('code')}")
    

urlpatterns = [
    path("", health, name="health-root"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),

    # ✅ allauth 라우트 등록 (필수)
    path("accounts/", include("allauth.urls")),  # ← 이거 추가

    # Google OAuth
    path("api/auth/google/code/", GoogleLoginCode.as_view(), name="google_login_code"),
    path("api/auth/google/callback/", google_callback_echo, name="google_callback_echo"),

    # GitHub OAuth
    path("api/auth/github/code/", GitHubLoginCode.as_view(), name="github_login_code"),
    path("api/auth/github/callback/", oauth_callback_echo, name="github_callback_echo"),

    # 로그인/회원가입 + dj-rest-auth
    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("api/auth/", include("dj_rest_auth.urls")),

    # 서비스 API
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),
]