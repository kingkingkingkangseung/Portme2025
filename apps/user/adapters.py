# apps/user/adapters.py
import re
import secrets
from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

User = get_user_model()

def _slug_base(s: str) -> str:
    s = (s or "user").strip()
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", s)
    return s or "user"

def _unique_username(base: str) -> str:
    base = _slug_base(base).lower()
    candidate = base[:20]
    i = 0
    while User.objects.filter(username=candidate).exists():
        i += 1
        suffix = f"_{i}"
        candidate = (base[:20 - len(suffix)] + suffix)[:20]
        if i > 50:  # 혹시나 무한루프 방지
            token = secrets.token_hex(2)
            candidate = (base[:20 - len(token) - 1] + "_" + token)[:20]
            break
    return candidate

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    - pre_social_login: 같은 이메일의 기존 유저가 있으면 자동 연결 (idempotent)
    - populate_user   : 최초 가입 시 username/풀네임 자동 세팅(비어있을 때만)
    """

    def pre_social_login(self, request, sociallogin):
        # 이미 연결되어 있으면 패스
        if sociallogin.is_existing:
            return

        # 이메일 최대한 튼튼하게 꺼내기
        email = None
        try:
            data = sociallogin.account.extra_data or {}
            email = data.get("email") or data.get("Email")
        except Exception:
            pass

        if not email:
            try:
                email = (sociallogin.user and sociallogin.user.email) or None
            except Exception:
                pass

        if not email and getattr(sociallogin, "email_addresses", None):
            try:
                verified = [e.email for e in sociallogin.email_addresses if getattr(e, "verified", False)]
                email = verified[0] if verified else sociallogin.email_addresses[0].email
            except Exception:
                pass

        if not email:
            # 이메일이 없으면 자동 연결 불가 → allauth 기본 흐름 진행
            return

        # 기존 유저 있으면 그 유저에 연결
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return

        try:
            with transaction.atomic():
                sociallogin.connect(request, user)
        except IntegrityError:
            # 경합으로 이미 연결됐으면 조용히 통과
            return

    def populate_user(self, request, sociallogin, data):
        """
        소셜 프로필 정보로 User 인스턴스 채움.
        username이 비어 있으면 구글 이름 기반으로 자동 생성.
        """
        user = super().populate_user(request, sociallogin, data)

        name = (
            (data or {}).get("name")
            or (data or {}).get("given_name")
            or (data or {}).get("family_name")
            or (getattr(user, "email", "") or "").split("@")[0]
            or "user"
        )

        if not getattr(user, "username", None):
            user.username = _unique_username(name)

        # 선택: 커스텀 필드가 있다면 채우기
        if hasattr(user, "full_name") and not getattr(user, "full_name", ""):
            user.full_name = name

        return user
# # apps/user/adapters.py
# from django.db import IntegrityError, transaction
# from django.contrib.auth import get_user_model
# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

# User = get_user_model()

# class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
#     """
#     소셜 최초 로그인 시, 같은 이메일의 기존 유저가 있으면
#     그 유저에 소셜 계정을 자동 연결한다 (idempotent).
#     """
#     def pre_social_login(self, request, sociallogin):
#         # 이미 연결되어 있으면 패스
#         if sociallogin.is_existing:
#             return

#         # 1) 이메일 최대한 튼튼하게 꺼내보기
#         email = None
#         try:
#             data = sociallogin.account.extra_data or {}
#             email = data.get("email") or data.get("Email")  # 혹시나 대소문자
#         except Exception:
#             pass

#         # 보조경로들
#         if not email:
#             try:
#                 email = (sociallogin.user and sociallogin.user.email) or None
#             except Exception:
#                 pass
#         if not email and getattr(sociallogin, "email_addresses", None):
#             try:
#                 # verified 우선
#                 verified = [e.email for e in sociallogin.email_addresses if getattr(e, "verified", False)]
#                 email = (verified[0] if verified else sociallogin.email_addresses[0].email)
#             except Exception:
#                 pass

#         if not email:
#             # 이메일이 없으면 자동연결 불가 → allauth 기본 흐름대로 진행
#             return

#         # 2) 기존 유저 있으면 그 유저에 연결
#         try:
#             user = User.objects.get(email__iexact=email)
#         except User.DoesNotExist:
#             return

#         # 경합 상황 대비 트랜잭션
#         try:
#             with transaction.atomic():
#                 sociallogin.connect(request, user)
#         except IntegrityError:
#             # 혹시 이미 다른 워커에서 붙였으면 조용히 통과
#             return

# # # apps/user/adapters.py
# # import re, secrets, string
# # from allauth.account.adapter import DefaultAccountAdapter
# # from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# # from django.contrib.auth import get_user_model

# # User = get_user_model()

# # # def _slugify_username_base(s: str) -> str:
# # #     s = s or "user"
# # #     s = s.lower()
# # #     s = re.sub(r"[^a-z0-9_]+", "_", s)
# # #     return s[:20] or "user"

# # # def _rand(n=6):
# # #     return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(n))

# # class CustomAccountAdapter(DefaultAccountAdapter):
# #     pass
# #     # """
# #     # 소셜/일반 회원가입 모두에서 username 비어있으면 안전하게 생성
# #     # """
# #     # def populate_username(self, request, user):
# #     #     # allauth가 내부에서 여러 번 호출하므로, 있으면 그대로 둔다
# #     #     if getattr(user, "username", None):
# #     #         return

# #     #     base = None
# #     #     # 이메일이 있으면 로컬파트 사용
# #     #     if getattr(user, "email", None):
# #     #         base = user.email.split("@")[0]

# #     #     base = _slugify_username_base(base)
# #     #     candidate = base
# #     #     from django.contrib.auth import get_user_model
# #     #     User = get_user_model()
# #     #     i = 0
# #     #     while User.objects.filter(username=candidate).exists():
# #     #         i += 1
# #     #         candidate = f"{base[:14]}_{_rand(5)}"
# #     #     user.username = candidate

# # class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
# #     """
# #     소셜 최초 로그인 시, 같은 이메일의 기존 유저가 있으면
# #     그 유저에 소셜 계정을 자동 연결한다.
# #     """
# #     def pre_social_login(self, request, sociallogin):
# #         # 이미 연결되어 있으면 패스
# #         if sociallogin.is_existing:
# #             return

# #         # 소셜 프로필에서 이메일 가져오기
# #         email = None
# #         try:
# #             email = sociallogin.account.extra_data.get("email")
# #         except Exception:
# #             pass
# #         if not email:
# #             return

# #         try:
# #             user = User.objects.get(email__iexact=email)
# #         except User.DoesNotExist:
# #             return

# #         # 기존 유저에 소셜 계정을 연결
# #         sociallogin.connect(request, user)