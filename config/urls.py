from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from rest_framework.routers import DefaultRouter
from apps.activity.views import AwardViewSet, CertificationViewSet, ForeignLangViewSet, GlobalExpViewSet

# user.views에서 필요한 뷰만 import
from apps.user.views import (
    CustomLoginView,
    CustomRegisterView,
    GoogleLogin,
    GoogleLoginCallback,
)

# 📌 Award / Certification API
from apps.activity.views import AwardViewSet, CertificationViewSet


# 헬스체크용 뷰
def health(request):
    return HttpResponse("OK")

<<<<<<< HEAD
def google_callback_echo(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"detail": "code not found"}, status=400)
    state = request.GET.get("state")
    return JsonResponse({"code": code, "state": state}, status=200)

def oauth_callback_echo(request):
    return HttpResponse(f"code = {request.GET.get('code')}")


# 📌 Award/Certification 전용 Router
router = DefaultRouter()
router.register(r"awards", AwardViewSet, basename="award")
router.register(r"certifications", CertificationViewSet, basename="certification")
router.register(r"globalexps", GlobalExpViewSet, basename="globalexp")
router.register(r"foreignlangs", ForeignLangViewSet, basename="foreignlang")


=======
>>>>>>> 1027
urlpatterns = [
    path("", health, name="health-root"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),

<<<<<<< HEAD
    # ✅ allauth 라우트 등록
    path("accounts/", include("allauth.urls")),

    # GOOGLE
    path("api/auth/google/login/", GoogleAuthStart.as_view(), name="google_auth_start"),
    path("api/auth/google/callback/", GoogleAuthCallback.as_view(), name="google_auth_callback"),

    # GITHUB
    path("api/auth/github/login/", GitHubAuthStart.as_view(), name="github_auth_start"),
    path("api/auth/github/callback/", GitHubAuthCallback.as_view(), name="github_auth_callback"),

    # 로그인/회원가입 + dj-rest-auth
=======
    path("accounts/", include("allauth.urls")),

    #GOOGLE
    path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"),
    path("api/v1/auth/google/callback/", GoogleLoginCallback.as_view(), name="google_login_callback"),

>>>>>>> 1027
    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("api/password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
    path("api/auth/", include("dj_rest_auth.urls")),

    # 서비스 API
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),   # 👉 Activity만
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),

    # ✅ Award/Certification 최상위 등록
    path("api/", include(router.urls)),
]
