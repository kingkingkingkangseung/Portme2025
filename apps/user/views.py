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

# --- allauth Google adapter ---
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client


class CustomRegisterView(RegisterView):
    """회원가입 후 access/refresh 토큰과 유저 정보를 반환"""
    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    user_data,
        }, status=status.HTTP_200_OK)


class CustomLoginView(LoginView):
    """로그인 후 access/refresh 토큰과 유저 정보를 반환"""
    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    user_data,
        }, status=status.HTTP_200_OK)


class GoogleLoginCode(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:8000/api/auth/google/code/'

    class FixedOAuth2Client(OAuth2Client):
        """scope_delimiter 중복 전달 문제를 방지한 래퍼 클래스"""
        def __init__(self, *args, **kwargs):
            kwargs.pop('scope_delimiter', None)
            super().__init__(*args, **kwargs)

    client_class = FixedOAuth2Client  # 클래스 속성으로 지정

    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    user_data,
        }, status=status.HTTP_200_OK)
