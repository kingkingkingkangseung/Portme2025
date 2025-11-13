# apps/user/views.py
from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from dj_rest_auth.serializers import UserDetailsSerializer

import secrets, string
import requests
from urllib.parse import urlencode
from urllib.parse import urljoin

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from django.conf import settings
from django.contrib.auth import get_user_model  
from django.utils import timezone
from django.shortcuts import redirect
from django.views import View
from django.shortcuts import render
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import BasicAuthentication  # (빈 auth 방지용 선택사항)


User = get_user_model()

# ==================== 공통 유틸 ====================

def _random_state(length=32):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def _issue_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}

def _ensure_username(base: str):
    base = base or "user"
    base = base.replace("@", "_").replace(".", "_")
    candidate = base[:20]
    i = 0
    while User.objects.filter(username=candidate).exists():
        i += 1
        candidate = f"{base[:15]}_{i}"
    return candidate

class CustomRegisterView(RegisterView):
    """
    회원가입 후 access/refresh 토큰과 유저 정보를 반환
    """
    permission_classes = [AllowAny]

    def get_response(self):
        try:
            if not getattr(self, "user", None):
                return Response({"detail": "registration user missing"}, status=400)
            refresh = RefreshToken.for_user(self.user)
            user_data = UserDetailsSerializer(self.user).data
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "registration response error", "error": str(e)}, status=500)


class CustomLoginView(LoginView):
    """
    로그인 후 access/refresh 토큰과 유저 정보를 반환
    """
    permission_classes = [AllowAny]

    def get_response(self):
        try:
            if not getattr(self, "user", None):
                return Response({"detail": "Invalid credentials"}, status=400)
            refresh = RefreshToken.for_user(self.user)
            user_data = UserDetailsSerializer(self.user).data
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # 안전망: 500 대신 친절한 메시지와 힌트 제공
            return Response({"detail": "login response error", "error": str(e)}, status=500)



# ==================== GOOGLE ====================
class GoogleLoginCode(SocialLoginView):
    """
    프론트에서 전달한 redirect_uri를 그대로 사용해 Authorization Code 교환.
    프론트 요청 형식: POST /api/v1/auth/google/ { code, redirect_uri }
    응답: { access, refresh, ... }
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # 기본 IsAuthenticated 무시
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = settings.GOOGLE_REDIRECT_URI  # 기본값 (없을 때 대비)

    def get_callback_url(self, request, *args, **kwargs):
        # 프론트가 보내준 redirect_uri가 있으면 그걸 우선 사용
        return request.data.get("redirect_uri") or request.query_params.get("redirect_uri") or self.callback_url

# if you want to use Authorization Code Grant, use this
# class GoogleLogin(SocialLoginView):
#     # Allow unauthenticated users to post authorization code
#     permission_classes = [AllowAny]
#     authentication_classes = []
#     adapter_class = GoogleOAuth2Adapter
#     callback_url = settings.GOOGLE_REDIRECT_URI
#     client_class = OAuth2Client


# class GoogleLoginCallback(APIView):
#     permission_classes = [AllowAny]
#     def get(self, request, *args, **kwargs):
#         """Accept callback request from Google OAuth screen.
#         Extract code and send a POST request to Google authentication endpoint.

#         If you are building a fullstack application (eg. with React app next to Django)
#         you can place this endpoint in your frontend application to receive
#         the JWT tokens there - and store them in the state
#         """

#         code = request.GET.get("code")

#         if code is None:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#         token_endpoint_url = request.build_absolute_uri(reverse("google_login"))

#         response = requests.post(url=token_endpoint_url, data={"code": code})

#         return Response(response.json(), status=status.HTTP_200_OK)

