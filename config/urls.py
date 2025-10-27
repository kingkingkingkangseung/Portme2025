from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter

from apps.activity.views import (
    AwardViewSet, CertificationViewSet, ForeignLangViewSet, GlobalExpViewSet
)
from apps.user.views import (
    CustomLoginView,
    CustomRegisterView,
    GoogleAuthStart, GoogleAuthCallback,
    GitHubAuthStart, GitHubAuthCallback,
)


def health(request):
    return HttpResponse("OK")


# Router for award/cert/globalexp/foreignlang
router = DefaultRouter()
router.register(r"awards", AwardViewSet, basename="award")
router.register(r"certifications", CertificationViewSet, basename="certification")
router.register(r"globalexps", GlobalExpViewSet, basename="globalexp")
router.register(r"foreignlangs", ForeignLangViewSet, basename="foreignlang")


urlpatterns = [
    path("", health, name="health-root"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),

    # allauth
    path("accounts/", include("allauth.urls")),

    # OAuth
    path("api/auth/google/login/", GoogleAuthStart.as_view(), name="google_auth_start"),
    path("api/auth/google/callback/", GoogleAuthCallback.as_view(), name="google_auth_callback"),
    path("api/auth/github/login/", GitHubAuthStart.as_view(), name="github_auth_start"),
    path("api/auth/github/callback/", GitHubAuthCallback.as_view(), name="github_auth_callback"),

    # Auth
    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("api/auth/", include("dj_rest_auth.urls")),

    # Apps
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),

    # Router endpoints
    path("api/", include(router.urls)),
]

