# apps/user/views.py

# --- Django REST Framework ---
from rest_framework.response import Response
from rest_framework import status

# --- Simple JWT ---
from rest_framework_simplejwt.tokens import RefreshToken

# --- dj-rest-auth views & serializers ---
from dj_rest_auth.registration.views import RegisterView, SocialLoginView
from dj_rest_auth.views import LoginView
from dj_rest_auth.serializers import UserDetailsSerializer

# --- allauth adapters ---
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter


# 버전 조합에 따라 scope_delimiter 인자 충돌을 막는 래퍼
class FixedOAuth2Client(OAuth2Client):
    def __init__(self, *args, **kwargs):
        kwargs.pop("scope_delimiter", None)
        super().__init__(*args, **kwargs)


class CustomRegisterView(RegisterView):
    """회원가입 후 access/refresh 토큰과 유저 정보를 반환"""
    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user":    user_data,
        }, status=status.HTTP_200_OK)


class CustomLoginView(LoginView):
    """로그인 후 access/refresh 토큰과 유저 정보를 반환"""
    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user":    user_data,
        }, status=status.HTTP_200_OK)


# -------- Google OAuth (Authorization Code) --------
class GoogleLoginCode(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class  = FixedOAuth2Client
    # 콘솔 Authorized redirect URIs 와 1자도 다르면 안 됨(끝 슬래시 포함)
    callback_url  = "http://localhost:8000/api/auth/google/code/"

    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user":    user_data,
        }, status=status.HTTP_200_OK)


# -------- GitHub OAuth (Authorization Code) --------
class GitHubLoginCode(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class  = FixedOAuth2Client
    # GitHub OAuth App 의 Authorization callback URL 과 동일하게
    callback_url  = "http://localhost:8000/api/auth/github/callback/"

    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user":    user_data,
        }, status=status.HTTP_200_OK)
