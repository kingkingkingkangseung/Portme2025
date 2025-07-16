from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'name',
            'birthdate',
            'certifications',
            'skills',
            'contact_info',
            'desired_job',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']  # 수정 불가능하게 설정