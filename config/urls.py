from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.http import JsonResponse

# user.views에서 필요한 뷰만 import
from apps.user.views import (
    CustomLoginView,
    CustomRegisterView,
    GoogleLogin,
    GoogleLoginCallback,
)

# 헬스체크용 뷰
def health(request):
    return HttpResponse("OK")

urlpatterns = [
    path("", health, name="health-root"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),

    path("accounts/", include("allauth.urls")),

    #GOOGLE
    path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"),
    path("api/v1/auth/google/callback/", GoogleLoginCallback.as_view(), name="google_login_callback"),

    path("api/auth/login/", CustomLoginView.as_view(), name="rest_login"),
    path("api/auth/registration/", CustomRegisterView.as_view(), name="rest_register"),
    path("api/password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
    path("api/auth/", include("dj_rest_auth.urls")),

    # 서비스 API
    path("api/profiles/", include("apps.profiles.urls")),
    path("api/activities/", include("apps.activity.urls")),
    path("api/portfolios/", include("apps.portfolio.urls")),
    path("api/community/", include("apps.community.urls")),
]