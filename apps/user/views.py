# apps/user/views.py

# --- Django/DRF utility ---
from rest_framework.response import Response
from rest_framework import status

# --- Simple JWT ---
from rest_framework_simplejwt.tokens import RefreshToken

# --- dj-rest-auth views & serializers ---
from dj_rest_auth.registration.views import RegisterView, SocialLoginView
from dj_rest_auth.views import LoginView
from dj_rest_auth.serializers import UserDetailsSerializer

# --- allauth Google adapter (Implicit & Code Grant) ---
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class CustomRegisterView(RegisterView):
    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    user_data,
        }, status=status.HTTP_200_OK)

class CustomLoginView(LoginView):
    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    user_data,
        }, status=status.HTTP_200_OK)

# ① Implicit Grant (프론트가 access_token 바로 POST)
class GoogleLoginImplicit(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def get_response(self):
        # 1) RefreshToken 생성
        refresh = RefreshToken.for_user(self.user)
        # 2) 사용자 정보 직렬화
        user_data = UserDetailsSerializer(self.user).data
        # 3) 원하는 JSON 형태로 반환
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    user_data,
        }, status=status.HTTP_200_OK)

# ② Authorization Code Grant (프론트가 code POST → 서버가 토큰 교환)
class GoogleLoginCode(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class  = OAuth2Client
    callback_url  = 'http://localhost:8000/api/auth/google/code/'

    def get_response(self):
        # 1) RefreshToken 생성
        refresh = RefreshToken.for_user(self.user)
        # 2) 유저 정보 직렬화
        user_data = UserDetailsSerializer(self.user).data
        # 3) 원하는 JSON 형태로 응답
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    user_data,
        }, status=status.HTTP_200_OK)