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
    GoogleLoginCode,
    #GoogleLogin, GoogleLoginCallback,
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

    # OAuth (current implementation uses SocialLoginView)
    path("api/v1/auth/google/", GoogleLoginCode.as_view(), name="google_login"),
    
    # path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"),
    # path("api/v1/auth/google/callback/", GoogleLoginCallback.as_view(), name="google_login_callback"),

    # Auth
    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("api/auth/", include("dj_rest_auth.urls")),
    # Password reset (django-rest-passwordreset)
    # Canonical include so endpoints are exactly:
    #   - /api/password_reset/
    #   - /api/password_reset/validate_token/
    #   - /api/password_reset/confirm/
    path("api/password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),

    # Apps
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),

    # Router endpoints
    path("api/", include(router.urls)),
]
