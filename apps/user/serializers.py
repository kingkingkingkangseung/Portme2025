# apps/user/serializers.py
from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer
from rest_framework import serializers

class RegisterSerializer(BaseRegisterSerializer):
    def __init__(self, *args, **kwargs):
        print("🚀 Custom RegisterSerializer __init__ 호출됨!")
        super().__init__(*args, **kwargs)
        # allauth 내부의 has_phone_field 체크 우회
        self._has_phone_field = False
