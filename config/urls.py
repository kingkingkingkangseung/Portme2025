from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ 로그인 / 로그아웃 / 토큰 갱신 등
    path('dj-rest-auth/', include('dj_rest_auth.urls')),

    # ✅ 회원가입용 (지금은 안 쓸 수도 있지만 일단 포함)
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),

    # ✅ 프로필 등 메인 API들
    path('api/profiles/', include('apps.profiles.urls')),

    # ✅ 활동 API
    path('api/activities/', include('apps.activity.urls')),

    # ✅ 포트폴리오 API
    path('api/portfolios/', include('apps.portfolio.urls')),
]