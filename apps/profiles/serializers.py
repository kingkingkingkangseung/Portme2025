# apps/profiles/serializers.py
from rest_framework import serializers

from .models import (
    Profile,
    JobRole,
    JobCategory,
    HardSkill,
    SoftSkill,
    JobHardSkill,
    JobSoftSkill,
    ProfileLink,
    Education,
)


class JobRoleSerializer(serializers.ModelSerializer):
    job_category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JobRole
        fields = ("id", "name", "group", "job_category")

    def get_job_category(self, obj):
        if not obj.job_category:
            return None
        return {
            "id": obj.job_category.id,
            "name": obj.job_category.name,
        }


class ProfileLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileLink
        fields = ("id", "label", "url", "order")


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            "id",
            "school_type",
            "school_name",
            "is_transfer",
            "start_year_month",
            "end_year_month",
            "status",
            "major_type",
            "major_name",
            "gpa",
            "gpa_scale",
        )


class ProfileSerializer(serializers.ModelSerializer):
    """
    - 응답:
        * job_role: nested 객체
        * links, educations: nested 리스트
    - 입력:
        * job_role_id 또는 job_role(int) 로 직무 설정
        * links, educations 전체 목록을 한번에 갱신
    """

    job_role = JobRoleSerializer(read_only=True)
    job_role_name = serializers.CharField(source="job_role.name", read_only=True)
    # 직무 텍스트(프로필 카드에 노출) → User 모델의 job_title 과 연결
    job_title = serializers.CharField(
        source="user.job_title", required=False, allow_blank=True
    )

    # 쓰기용 필드: id 기반으로 직무 지정
    job_role_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    # 링크/학력: 읽기/쓰기 모두 같은 구조 사용
    links = ProfileLinkSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)

    class Meta:
        model = Profile
        fields = [
            "id",
            # 기본 프로필
            "display_name",
            "bio",
            "avatar",
            "website",
            # 프로필 카드
            "full_name",
            "github_linked",
            "level",
            "job_title",
            # 추가 입력 필드
            "birth_date",
            "phone_number",
            "email",
            # 직무
            "job_role",
            "job_role_name",
            "job_role_id",
            # 링크/학력
            "links",
            "educations",
            # 메타
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job_role",
            "job_role_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        """
        - job_role_id 가 있으면 우선 사용
        - 없으면 initial_data 의 job_role 가 int 인지 검사
        - 유효하지 않은 직무 id 이면 400
        """
        role_id = attrs.pop("job_role_id", None)

        # 'job_role': <int> 형태로 들어온 경우 지원
        if role_id is None:
            raw = self.initial_data.get("job_role")
            if isinstance(raw, int):
                role_id = raw

        if role_id is not None:
            if role_id == "" or role_id is False:
                role_id = None

        if role_id is not None:
            try:
                role_obj = JobRole.objects.get(pk=role_id, is_active=True)
            except JobRole.DoesNotExist:
                raise serializers.ValidationError(
                    {"job_role_id": "유효한 직무가 아닙니다."}
                )
            attrs["job_role"] = role_obj
        elif "job_role" in attrs and attrs["job_role"] is None:
            # 명시적으로 null 을 보낸 경우
            attrs["job_role"] = None

        return attrs

    # ---------- nested write helpers ----------

    def _sync_links(self, profile: Profile, links_data):
        if links_data is None:
            return
        ProfileLink.objects.filter(profile=profile).delete()
        to_create = []
        for idx, item in enumerate(links_data):
            url = item.get("url")
            if not url:
                continue
            order = item.get("order", idx)
            to_create.append(
                ProfileLink(
                    profile=profile,
                    label=item.get("label", ""),
                    url=url,
                    order=order,
                )
            )
        if to_create:
            ProfileLink.objects.bulk_create(to_create)

    def _sync_educations(self, profile: Profile, edu_data):
        if edu_data is None:
            return
        Education.objects.filter(profile=profile).delete()
        to_create = []
        for item in edu_data:
            # 최소한 학교명은 있어야 저장
            if not item.get("school_name"):
                continue
            to_create.append(
                Education(
                    profile=profile,
                    school_type=item.get("school_type") or Education.SchoolType.UNIV_4,
                    school_name=item.get("school_name"),
                    is_transfer=item.get("is_transfer", False),
                    start_year_month=item.get("start_year_month", ""),
                    end_year_month=item.get("end_year_month", ""),
                    status=item.get("status") or Education.Status.ENROLLED,
                    major_type=item.get("major_type", ""),
                    major_name=item.get("major_name", ""),
                    gpa=item.get("gpa"),
                    gpa_scale=item.get("gpa_scale"),
                )
            )
        if to_create:
            Education.objects.bulk_create(to_create)

    def create(self, validated_data):
        links_data = validated_data.pop("links", None)
        edu_data = validated_data.pop("educations", None)
        user_data = validated_data.pop("user", {})
        job_title = user_data.get("job_title")

        profile = super().create(validated_data)

        if job_title is not None:
            profile.user.job_title = job_title
            profile.user.save(update_fields=["job_title"])

        self._sync_links(profile, links_data)
        self._sync_educations(profile, edu_data)
        return profile

    def update(self, instance, validated_data):
        links_data = validated_data.pop("links", None)
        edu_data = validated_data.pop("educations", None)
        user_data = validated_data.pop("user", {})
        job_title = user_data.get("job_title")

        profile = super().update(instance, validated_data)

        if job_title is not None:
            profile.user.job_title = job_title
            profile.user.save(update_fields=["job_title"])

        self._sync_links(profile, links_data)
        self._sync_educations(profile, edu_data)
        return profile


# ---------- ERD 확장 직무/스킬 ----------


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ("id", "name", "order")


class HardSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardSkill
        fields = ("id", "name", "code")


class SoftSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftSkill
        fields = ("id", "name")


class JobRoleSkillsSerializer(serializers.Serializer):
    job_role = JobRoleSerializer(read_only=True)
    hard_skills = HardSkillSerializer(many=True, read_only=True)
    soft_skills = SoftSkillSerializer(many=True, read_only=True)


class JobRoleSkillsUpdateSerializer(serializers.Serializer):
    hard_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    soft_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
