# apps/user/adapters.py
import re, secrets, string
from allauth.account.adapter import DefaultAccountAdapter

def _slugify_username_base(s: str) -> str:
    s = s or "user"
    s = s.lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return s[:20] or "user"

def _rand(n=6):
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(n))

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    소셜/일반 회원가입 모두에서 username 비어있으면 안전하게 생성
    """
    def populate_username(self, request, user):
        # allauth가 내부에서 여러 번 호출하므로, 있으면 그대로 둔다
        if getattr(user, "username", None):
            return

        base = None
        # 이메일이 있으면 로컬파트 사용
        if getattr(user, "email", None):
            base = user.email.split("@")[0]

        base = _slugify_username_base(base)
        candidate = base
        from django.contrib.auth import get_user_model
        User = get_user_model()
        i = 0
        while User.objects.filter(username=candidate).exists():
            i += 1
            candidate = f"{base[:14]}_{_rand(5)}"
        user.username = candidate

# # apps/user/adapters.py
# from allauth.account.adapter import DefaultAccountAdapter

# class CustomAccountAdapter(DefaultAccountAdapter):
#     def save_user(self, request, user, form, commit=True):
#         """
#         form이 allauth 폼이 아니라 dj-rest-auth의 RegisterSerializer인 경우를 처리하도록 오버라이드
#         """
#         # form이 serializer라면 validated_data에서, 아니면 form.cleaned_data에서 가져오기
#         data = {}
#         if hasattr(form, 'validated_data'):
#             data = form.validated_data
#         else:
#             data = form.cleaned_data

#         # 필수 필드 세팅
#         user.username = data.get('username', '')
#         user.email = data.get('email', '')

#         # 비밀번호 세팅 (allauth의 기본 로직을 쓸 수도 있지만, 안전하게 직접)
#         password = data.get('password1') or data.get('password')
#         if password:
#             user.set_password(password)

#         # phone 필드가 있으면 저장
#         phone = data.get('phone')
#         if phone:
#             user.phone = phone

#         # 기타 추가 필드도 여기에…

#         if commit:
#             user.save()
#         return user
