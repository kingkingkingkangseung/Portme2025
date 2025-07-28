from django.contrib import admin
from django.urls import path, include

from apps.user.views import (
    GoogleLoginImplicit,
    GoogleLoginCode,
    CustomLoginView,
    CustomRegisterView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1) Google Implicit Grant
    path(
        'api/auth/google/implicit/',
        GoogleLoginImplicit.as_view(),
        name='google_login_implicit'
    ),

    # 2) Google Authorization Code Grant
    path(
        'api/auth/google/code/',
        GoogleLoginCode.as_view(),
        name='google_login_code'
    ),

    # Custom login & registration (overrides default dj-rest-auth)
    path('api/auth/login/', CustomLoginView.as_view(), name='rest_login'),
    path('api/auth/registration/', CustomRegisterView.as_view(), name='rest_register'),

    # dj-rest-auth endpoints (login/logout/token refresh)
    path('api/auth/', include('dj_rest_auth.urls')),

    # allauth social account URLs
    path('api/social/', include('allauth.socialaccount.urls')),

    # Profile, Activity, Portfolio, Community APIs
    path('api/profiles/', include('apps.profiles.urls')),
    path('api/activities/', include('apps.activity.urls')),
    path('api/portfolios/', include('apps.portfolio.urls')),
    path('api/community/', include('apps.community.urls')),
]
