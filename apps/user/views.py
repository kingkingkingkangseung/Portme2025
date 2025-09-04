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

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user_data,
        }, status=status.HTTP_200_OK)


class CustomLoginView(LoginView):
    """
    로그인 후 access/refresh 토큰과 유저 정보를 반환
    """
    permission_classes = [AllowAny]

    def get_response(self):
        refresh = RefreshToken.for_user(self.user)
        user_data = UserDetailsSerializer(self.user).data
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user_data,
        }, status=status.HTTP_200_OK)



# ==================== GOOGLE ====================

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

class GoogleAuthStart(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        state = _random_state()
        request.session["oauth_state_google"] = state
        request.session["oauth_state_google_ts"] = timezone.now().isoformat()

        params = {
            "response_type": "code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return redirect(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


class GoogleAuthCallback(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code or not state:
            return Response({"detail": "code/state 누락"}, status=400)

        if state != request.session.get("oauth_state_google"):
            return Response({"detail": "state 불일치"}, status=400)

        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_res = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
        if token_res.status_code != 200:
            return Response({"detail": "Google 토큰 교환 실패", "res": token_res.text}, status=400)

        token_json = token_res.json()
        access_token = token_json.get("access_token")
        id_token = token_json.get("id_token")

        userinfo = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        ).json()

        email = userinfo.get("email")
        sub = userinfo.get("sub")
        name = userinfo.get("name") or ""
        if not email:
            return Response({"detail": "Google에서 이메일을 제공하지 않았습니다."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            username = _ensure_username(email.split("@")[0] or f"g_{sub[:8]}")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,
            )
            user.first_name = name[:30]
            user.set_unusable_password()
            user.save()

        tokens = _issue_jwt_for_user(user)
        return Response({
            "provider": "google",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "name": user.first_name,
            },
            "tokens": tokens,
            "raw": {"id_token": id_token},
        }, status=200)


# ==================== GITHUB ====================

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

class GitHubAuthStart(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        state = _random_state()
        request.session["oauth_state_github"] = state
        request.session["oauth_state_github_ts"] = timezone.now().isoformat()

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "read:user user:email",
            "state": state,
            "allow_signup": "true",
        }
        return redirect(f"{GITHUB_AUTH_URL}?{urlencode(params)}")


class GitHubAuthCallback(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code or not state:
            return Response({"detail": "code/state 누락"}, status=400)
        if state != request.session.get("oauth_state_github"):
            return Response({"detail": "state 불일치"}, status=400)

        headers = {"Accept": "application/json"}
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "state": state,
        }
        token_res = requests.post(GITHUB_TOKEN_URL, headers=headers, data=data, timeout=10)
        if token_res.status_code != 200:
            return Response({"detail": "GitHub 토큰 교환 실패", "res": token_res.text}, status=400)

        token_json = token_res.json()
        access_token = token_json.get("access_token")

        u = requests.get(GITHUB_USER_URL, headers={"Authorization": f"Bearer {access_token}"}, timeout=10).json()
        emails = requests.get(GITHUB_EMAILS_URL, headers={"Authorization": f"Bearer {access_token}"}, timeout=10).json()

        email = None
        if isinstance(emails, list):
            primaries = [e for e in emails if e.get("primary") and e.get("verified")]
            if primaries:
                email = primaries[0].get("email")
            elif emails:
                email = emails[0].get("email")

        if not email:
            return Response({"detail": "GitHub 이메일 확인 실패. 이메일이 비공개 상태이거나 인증되지 않았습니다."}, status=400)

        login = (u.get("login") or "gh_user")
        name = (u.get("name") or "")[:30]
        gid = str(u.get("id") or "")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            username = _ensure_username(login or f"gh_{gid[:8]}")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None,
            )
            user.first_name = name
            user.set_unusable_password()
            user.save()

        tokens = _issue_jwt_for_user(user)
        return Response({
            "provider": "github",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "name": user.first_name,
            },
            "tokens": tokens,
        }, status=200)
