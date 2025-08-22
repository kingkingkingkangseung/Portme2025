# apps/profiles/serializers.py
from rest_framework import serializers
from .models import Profile, JobRole


class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = ("id", "name", "group")


class ProfileSerializer(serializers.ModelSerializer):
    # 응답용(읽기): 직무를 nested 로 보여줌
    job_role = JobRoleSerializer(read_only=True)
    job_role_name = serializers.CharField(source="job_role.name", read_only=True)

    # 입력용(쓰기): 두 키 모두 지원
    # 1) job_role_id: 25
    job_role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # 2) job_role: 25  (정수로 오면 alias 처리를 해줌; 응답에서는 nested로 나감)
    #    → 별도 필드 정의 없이 validate()에서 initial_data를 보고 처리

    class Meta:
        model = Profile
        fields = [
            "id",
            # 기본 프로필
            "display_name", "bio", "avatar", "website",
            # 사용자 카드
            "full_name", "github_linked", "level",
            # 직무
            "job_role", "job_role_name", "job_role_id",
            # 메타
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        - job_role_id 를 우선 사용
        - 없으면 initial_data 의 job_role 이 int 로 온 경우도 허용
        - 유효하지 않은 id 이면 400 에러
        """
        # 1) job_role_id 우선
        role_id = attrs.pop("job_role_id", None)

        # 2) 'job_role': <int> 로 왔는지도 체크 (응답에서 nested로 쓰는 필드지만, 입력 alias 허용)
        if role_id is None:
            raw = self.initial_data.get("job_role", None)
            if isinstance(raw, int):
                role_id = raw

        if role_id is not None:
            if role_id == "" or role_id is False:
                role_id = None

        if role_id is not None:
            try:
                role_obj = JobRole.objects.get(pk=role_id, is_active=True)
            except JobRole.DoesNotExist:
                raise serializers.ValidationError({"job_role_id": "유효한 직무가 아닙니다."})
            # 모델 필드에 직접 매핑
            attrs["job_role"] = role_obj
        elif "job_role" in attrs and attrs["job_role"] is None:
            # 명시적으로 null 로 보낸 경우 (ex. job_role_id: null)
            attrs["job_role"] = None

        return attrs
