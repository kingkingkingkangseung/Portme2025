# apps/user/adapters.py
import re, secrets, string
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

# def _slugify_username_base(s: str) -> str:
#     s = s or "user"
#     s = s.lower()
#     s = re.sub(r"[^a-z0-9_]+", "_", s)
#     return s[:20] or "user"

# def _rand(n=6):
#     return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(n))

class CustomAccountAdapter(DefaultAccountAdapter):
    pass
    # """
    # 소셜/일반 회원가입 모두에서 username 비어있으면 안전하게 생성
    # """
    # def populate_username(self, request, user):
    #     # allauth가 내부에서 여러 번 호출하므로, 있으면 그대로 둔다
    #     if getattr(user, "username", None):
    #         return

    #     base = None
    #     # 이메일이 있으면 로컬파트 사용
    #     if getattr(user, "email", None):
    #         base = user.email.split("@")[0]

    #     base = _slugify_username_base(base)
    #     candidate = base
    #     from django.contrib.auth import get_user_model
    #     User = get_user_model()
    #     i = 0
    #     while User.objects.filter(username=candidate).exists():
    #         i += 1
    #         candidate = f"{base[:14]}_{_rand(5)}"
    #     user.username = candidate

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    소셜 최초 로그인 시, 같은 이메일의 기존 유저가 있으면
    그 유저에 소셜 계정을 자동 연결한다.
    """
    def pre_social_login(self, request, sociallogin):
        # 이미 연결되어 있으면 패스
        if sociallogin.is_existing:
            return

        # 소셜 프로필에서 이메일 가져오기
        email = None
        try:
            email = sociallogin.account.extra_data.get("email")
        except Exception:
            pass
        if not email:
            return

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return

        # 기존 유저에 소셜 계정을 연결
        sociallogin.connect(request, user)