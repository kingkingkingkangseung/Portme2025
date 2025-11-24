# apps/user/views.py

from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from dj_rest_auth.serializers import UserDetailsSerializer

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

import secrets
import string
import requests
import logging
import traceback


User = get_user_model()
logger = logging.getLogger(__name__)


# ==================== 공통 유틸 ====================

def _issue_jwt_for_user(user):
    """
    우리 서비스용 JWT(access/refresh) 발급.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def _ensure_username(base: str):
    """
    구글 이름/이메일 기반으로 username을 안전하게 생성.
    (중복 있으면 _1, _2 ... 붙여서 유니크하게)
    """
    base = (base or "user").strip()
    base = base.replace("@", "_").replace(".", "_")
    candidate = base[:20]
    i = 0
    while User.objects.filter(username=candidate).exists():
        i += 1
        candidate = f"{base[:15]}_{i}"
    return candidate


# ==================== 회원가입 / 로그인 (기존 유지) ====================

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
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": user_data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": "registration response error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": user_data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": "login response error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================== GOOGLE (code 교환 X, token 기반) ====================

class GoogleLoginCode(APIView):
    """
    프론트에서 이미 받아온 Google access_token 또는 id_token을 받아서
    - 구글에 검증 요청
    - User 생성/조회
    - 우리 서비스용 JWT 발급

    요청 형식 (예시):
        POST /api/v1/auth/google/
        {
            "access_token": "<구글 액세스 토큰>"   // 또는
            "id_token": "<구글 ID 토큰>"
        }

    응답 형식:
        {
            "access": "...",        # JWT access
            "refresh": "...",       # JWT refresh
            "user": { ... }         # UserDetailsSerializer 결과
        }
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # 비로그인 상태에서 접근 가능하도록

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri")
        code_verifier = request.data.get("code_verifier")
        access_token = request.data.get("access_token")
        id_token = request.data.get("id_token")

        if code:
            try:
                logger.info("google code exchange", extra={"code_prefix": (code or "")[:12], "redirect_uri": redirect_uri})
                token_payload = self._exchange_code_for_tokens(code, redirect_uri, code_verifier)
                access_token = token_payload.get("access_token")
                id_token = token_payload.get("id_token")
            except Exception as exc:
                logger.exception("GoogleLoginCode code exchange error")
                return Response(
                    {"detail": "google exchange failed", "error": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not access_token and not id_token:
            return Response(
                {"detail": "access_token 또는 id_token 중 하나는 반드시 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            google_data = self._get_google_userinfo(access_token, id_token)
        except Exception as e:
            logger.exception("GoogleLoginCode token validation error")
            return Response(
                {
                    "detail": "google token 검증 실패",
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = google_data.get("email")
        if not email:
            return Response(
                {
                    "detail": "구글 응답에 email이 없습니다.",
                    "google_response": google_data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이름 정보 최대한 잘 뽑기
        name = (
            google_data.get("name")
            or (
                (google_data.get("given_name", "") + " " + google_data.get("family_name", "")).strip()
            )
            or email.split("@")[0]
        )

        # ==== User 조회/생성 ====
        try:
            user = User.objects.get(email__iexact=email)
            created = False
        except User.DoesNotExist:
            username_base = email.split("@")[0] or name
            username = _ensure_username(username_base)
            # create_user 사용 (비밀번호는 랜덤으로 생성해도 되고, 빈 문자열 허용 모델이면 그대로 둬도 됨)
            user = User.objects.create_user(
                email=email,
                username=username,
                password=None,  # 소셜 전용 계정이라면 password=None 로 두고, 일반 로그인은 막아도 됨
            )
            created = True

        # full_name 같은 프로필 필드 채우기
        if hasattr(user, "full_name") and (not getattr(user, "full_name", None)) and name:
            user.full_name = name
            user.save(update_fields=["full_name"])

        # ==== JWT 발급 ====
        tokens = _issue_jwt_for_user(user)
        user_data = UserDetailsSerializer(user).data

        return Response(
            {
                **tokens,
                "user": user_data,
                "created": created,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------ 내부 헬퍼 ------------------

    def _get_google_userinfo(self, access_token: str | None, id_token: str | None) -> dict:
        """
        - id_token 이 있으면 tokeninfo 엔드포인트로 검증
        - 없고 access_token만 있으면 userinfo 엔드포인트 호출
        둘 다 구글에 'code 교환'이 아니라, 이미 발급된 토큰의 유효성 검증만 함.
        """
        # 1) ID 토큰이 있는 경우: tokeninfo(id_token=...) 으로 검증
        if id_token:
            resp = requests.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
                timeout=5,
            )
            data = resp.json()
            if resp.status_code != 200:
                raise Exception(f"tokeninfo(id_token) error: {data}")

            # aud 검증 (우리 앱의 client_id와 맞는지)
            aud = data.get("aud")
            if settings.GOOGLE_CLIENT_ID and aud != settings.GOOGLE_CLIENT_ID:
                raise Exception(f"Invalid aud: {aud}")

            return data

        # 2) access_token 만 있는 경우: userinfo 엔드포인트로 유저 정보 가져오기
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers=headers,
            timeout=5,
        )
        data = resp.json()
        if resp.status_code != 200:
            raise Exception(f"userinfo(access_token) error: {data}")

        # 필요하다면 여기서도 aud 검증을 위해 tokeninfo(access_token=...) 한번 더 호출 가능
        return data

    def _exchange_code_for_tokens(
        self, code: str, redirect_uri: str | None, code_verifier: str | None
    ) -> dict:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise Exception("google client 설정이 없습니다.")

        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri or settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        if code_verifier:
            payload["code_verifier"] = code_verifier

        resp = requests.post("https://oauth2.googleapis.com/token", data=payload, timeout=5)
        data = resp.json()
        if resp.status_code != 200:
            raise Exception(f"token 교환 실패: {data}")
        return data
