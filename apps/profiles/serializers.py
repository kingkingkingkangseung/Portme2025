# apps/profiles/serializers.py
from rest_framework import serializers
from .models import Profile, JobRole

class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = ("id", "name", "group")

class ProfileSerializer(serializers.ModelSerializer):
    job_role = JobRoleSerializer(read_only=True)
    job_role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            # 기본 프로필
            "display_name", "bio", "avatar", "website",
            # 사용자 카드
            "full_name", "github_linked", "level",
            "job_role", "job_role_id",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        job_role_id = validated_data.pop("job_role_id", None)
        if job_role_id is not None:
            instance.job_role = JobRole.objects.filter(pk=job_role_id).first()
        return super().update(instance, validated_data)
