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

import requests
import logging

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


# ==================== GOOGLE (Authorization Code + PKCE 지원) ====================

class GoogleLoginCode(APIView):
    """
    프론트에서 받은 Google authorization code (및 PKCE code_verifier)를
    서버에서 access_token/id_token 으로 교환하고,
    User 생성/조회 후 우리 서비스용 JWT를 발급한다.

    요청 형식:
        POST /api/v1/auth/google/
        {
            "code": "<auth code>",
            "redirect_uri": "https://grove.ajousw.kr/auth/google/callback",
            "code_verifier": "<PKCE code_verifier>"   // 선택 (PKCE 사용 시)
        }

    응답 형식:
        {
            "access": "...",        # JWT access
            "refresh": "...",       # JWT refresh
            "user": { ... },        # UserDetailsSerializer 결과
            "created": true/false   # 새로 만든 유저인지 여부
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

        # 1) Authorization Code → token 교환 (우리 플로우의 기본 케이스)
        if code:
            try:
                logger.info(
                    "GoogleLoginCode: code exchange 시작",
                    extra={
                        "code_prefix": (code or "")[:12],
                        "frontend_redirect_uri": redirect_uri,
                    },
                )
                token_payload = self._exchange_code_for_tokens(
                    code,
                    redirect_uri,
                    code_verifier,
                )
                access_token = token_payload.get("access_token")
                id_token = token_payload.get("id_token")
            except Exception as exc:
                logger.exception("GoogleLoginCode code exchange error")
                return Response(
                    {"detail": "google exchange failed", "error": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 2) 토큰이 전혀 없다면 에러
        if not access_token and not id_token:
            return Response(
                {"detail": "access_token 또는 id_token 중 하나는 반드시 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3) 구글 토큰 검증 + 유저 정보 가져오기
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

        # 4) 이름 정보 최대한 잘 뽑기
        name = (
            google_data.get("name")
            or (
                (google_data.get("given_name", "") + " " + google_data.get("family_name", "")).strip()
            )
            or email.split("@")[0]
        )

        # 5) User 조회/생성
        try:
            user = User.objects.get(email__iexact=email)
            created = False
        except User.DoesNotExist:
            username_base = email.split("@")[0] or name
            username = _ensure_username(username_base)
            user = User.objects.create_user(
                email=email,
                username=username,
                password=None,  # 소셜 전용 계정
            )
            created = True

        # full_name 같은 필드 채우기 (있을 경우)
        if hasattr(user, "full_name") and (not getattr(user, "full_name", None)) and name:
            user.full_name = name
            user.save(update_fields=["full_name"])

        # 6) JWT 발급
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
        - id_token 이 있으면 tokeninfo(id_token=...) 로 검증
        - 없고 access_token만 있으면 userinfo 엔드포인트 호출
        """
        # 1) ID 토큰이 있는 경우
        if id_token:
            resp = requests.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
                timeout=5,
            )
            data = resp.json()
            if resp.status_code != 200:
                raise Exception(f"tokeninfo(id_token) error: {data}")

            # aud 검증 (우리 client_id와 일치하는지)
            aud = data.get("aud")
            if settings.GOOGLE_CLIENT_ID and aud != settings.GOOGLE_CLIENT_ID:
                raise Exception(f"Invalid aud: {aud}")

            return data

        # 2) access_token만 있는 경우
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers=headers,
            timeout=5,
        )
        data = resp.json()
        if resp.status_code != 200:
            raise Exception(f"userinfo(access_token) error: {data}")

        return data

    def _exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str | None,
        code_verifier: str | None,
    ) -> dict:
        """
        Authorization Code + (선택) PKCE code_verifier 를 사용해서
        구글 토큰 엔드포인트로 access_token / id_token 을 교환한다.
        """

        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise Exception("google client 설정이 없습니다.")

        # 항상 서버 설정값을 기준으로 사용
        final_redirect_uri = settings.GOOGLE_REDIRECT_URI
        if redirect_uri and redirect_uri != final_redirect_uri:
            logger.warning(
                "GoogleLoginCode: redirect_uri mismatch (프론트 vs 서버 설정)",
                extra={
                    "frontend_redirect_uri": redirect_uri,
                    "settings_redirect_uri": final_redirect_uri,
                },
            )

        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": final_redirect_uri,
            "grant_type": "authorization_code",
        }

        if code_verifier:
            payload["code_verifier"] = code_verifier

        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data=payload,
            timeout=5,
        )
        data = resp.json()

        if resp.status_code != 200:
            raise Exception(f"token 교환 실패: {data}")

        return data