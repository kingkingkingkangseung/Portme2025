from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from rest_framework.routers import DefaultRouter

# user.views
from apps.user.views import (
    CustomLoginView,
    CustomRegisterView,
    GoogleAuthStart, GoogleAuthCallback,
    GitHubAuthStart, GitHubAuthCallback,
)

# activity.views (Router용 ViewSet들)
from apps.activity.views import (
    AwardViewSet, CertificationViewSet,
    GlobalExpViewSet, ForeignLangViewSet
)

# ===== 헬스체크 뷰 =====
def health(request):
    return HttpResponse("OK")

def google_callback_echo(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"detail": "code not found"}, status=400)
    state = request.GET.get("state")
    return JsonResponse({"code": code, "state": state}, status=200)

def oauth_callback_echo(request):
    return HttpResponse(f"code = {request.GET.get('code')}")

# ===== 📌 Router 등록 =====
router = DefaultRouter()
router.register(r"awards", AwardViewSet, basename="award")
router.register(r"certifications", CertificationViewSet, basename="certification")
router.register(r"globalexps", GlobalExpViewSet, basename="globalexp")
router.register(r"foreignlangs", ForeignLangViewSet, basename="foreignlang")

# ===== 📌 URL 패턴 =====
urlpatterns = [
    path("", health, name="health-root"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),

    # allauth
    path("accounts/", include("allauth.urls")),

    # Auth (Google/GitHub + dj-rest-auth)
    path("api/auth/google/login/", GoogleAuthStart.as_view(), name="google_auth_start"),
    path("api/auth/google/callback/", GoogleAuthCallback.as_view(), name="google_auth_callback"),
    path("api/auth/github/login/", GitHubAuthStart.as_view(), name="github_auth_start"),
    path("api/auth/github/callback/", GitHubAuthCallback.as_view(), name="github_auth_callback"),
    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("api/auth/", include("dj_rest_auth.urls")),

    # 서비스 API
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),  # Activity 전용 API
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),

    # 📌 Award / Certification / GlobalExp / ForeignLang 전용 Router
    path("api/", include(router.urls)),
]
