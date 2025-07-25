# """
# URL configuration for config project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin

from django.urls import path, include
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from apps.user.views import CustomLoginView, CustomRegisterView

from apps.user.views import (
    GoogleLoginImplicit,
    GoogleLoginCode,
    CustomLoginView,
    CustomRegisterView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1) Implicit Grant
    path(
      'api/auth/google/implicit/',
      GoogleLoginImplicit.as_view(),
      name='google_login_implicit'
    ),

    # 2) Authorization Code Grant
    path(
      'api/auth/google/code/',
      GoogleLoginCode.as_view(),
      name='google_login_code'
    ),

    # 🔁 커스텀 로그인 뷰 연결 (기존 login 덮어쓰기)
    path('api/auth/login/', CustomLoginView.as_view(), name='rest_login'),
    path('api/auth/registration/', CustomRegisterView.as_view(), name='rest_register'),
    
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/social/', include('allauth.socialaccount.urls')),
]