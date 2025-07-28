# apps/user/adapters.py
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        form이 allauth 폼이 아니라 dj-rest-auth의 RegisterSerializer인 경우를 처리하도록 오버라이드
        """
        # form이 serializer라면 validated_data에서, 아니면 form.cleaned_data에서 가져오기
        data = {}
        if hasattr(form, 'validated_data'):
            data = form.validated_data
        else:
            data = form.cleaned_data

        # 필수 필드 세팅
        user.username = data.get('username', '')
        user.email = data.get('email', '')

        # 비밀번호 세팅 (allauth의 기본 로직을 쓸 수도 있지만, 안전하게 직접)
        password = data.get('password1') or data.get('password')
        if password:
            user.set_password(password)

        # phone 필드가 있으면 저장
        phone = data.get('phone')
        if phone:
            user.phone = phone

        # 기타 추가 필드도 여기에…

        if commit:
            user.save()
        return user
