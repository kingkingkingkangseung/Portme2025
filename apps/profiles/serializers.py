# apps/profiles/serializers.py
from rest_framework import serializers

from .models import (
<<<<<<< HEAD
    Profile,
    JobRole,
    JobCategory,
    HardSkill,
    SoftSkill,
    JobHardSkill,
    JobSoftSkill,
    ProfileLink,
    Education,
=======
    Profile, JobRole, ProfileLink,
    JobCategory, HardSkill, SoftSkill,
    JobHardSkill, JobSoftSkill,
>>>>>>> eabf36c ( migrations 수정)
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


class ProfileLinkWriteSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=50, required=False, allow_blank=True)
    url = serializers.URLField()
    order = serializers.IntegerField(required=False, min_value=0)


class ProfileSerializer(serializers.ModelSerializer):
<<<<<<< HEAD
    """
    - 응답:
        * job_role: nested 객체
        * links, educations: nested 리스트
    - 입력:
        * job_role_id 또는 job_role(int) 로 직무 설정
    """

    job_role = JobRoleSerializer(read_only=True)
    job_role_name = serializers.CharField(source="job_role.name", read_only=True)

    # 쓰기용 필드: id 기반으로 직무 지정
    job_role_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    # 링크/학력: 읽기 전용 nested
    links = serializers.SerializerMethodField(read_only=True)
    educations = serializers.SerializerMethodField(read_only=True)
=======
    job_role = JobRoleSerializer(read_only=True)
    job_role_name = serializers.CharField(source="job_role.name", read_only=True)
    job_role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    links = ProfileLinkSerializer(many=True, read_only=True)
    link_items = ProfileLinkWriteSerializer(many=True, write_only=True, required=False)
>>>>>>> eabf36c ( migrations 수정)

    class Meta:
        model = Profile
        fields = [
            "id",
<<<<<<< HEAD
            # 기본 프로필
            "display_name",
            "bio",
            "avatar",
            "website",
            # 프로필 카드
            "full_name",
            "github_linked",
            "level",
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
            "links",
            "educations",
            "created_at",
            "updated_at",
        ]
=======
            "full_name", "bio", "avatar",
            "birth_date", "phone_number", "contact_email",
            "school_name", "admission_date", "graduation_date",
            "job_role", "job_role_name", "job_role_id",
            "links", "link_items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "job_role", "job_role_name", "links"]
        extra_kwargs = {
            "contact_email": {"allow_blank": True, "required": False},
            "phone_number": {"allow_blank": True, "required": False},
            "full_name": {"required": False},
            "bio": {"required": False},
        }
>>>>>>> eabf36c ( migrations 수정)

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

<<<<<<< HEAD
    def get_links(self, obj: Profile):
        qs = obj.links.all().order_by("order", "id")
        return [
            {
                "id": link.id,
                "title": link.title,
                "url": link.url,
                "order": link.order,
            }
            for link in qs
        ]

    def get_educations(self, obj: Profile):
        qs = obj.educations.all().order_by("-updated_at", "-id")
        return [
            {
                "id": edu.id,
                "school_type": edu.school_type,
                "school_name": edu.school_name,
                "is_transfer": edu.is_transfer,
                "start_year_month": edu.start_year_month,
                "end_year_month": edu.end_year_month,
                "status": edu.status,
                "major_type": edu.major_type,
                "major_name": edu.major_name,
                "gpa": edu.gpa,
                "gpa_scale": edu.gpa_scale,
            }
            for edu in qs
        ]
=======
    def _sync_links(self, profile: Profile, link_items):
        if link_items is None:
            return
        profile.links.all().delete()
        new_links = []
        for idx, payload in enumerate(link_items):
            url = payload.get("url")
            if not url:
                continue
            order = payload.get("order")
            if order is None:
                order = idx
            new_links.append(
                ProfileLink(
                    profile=profile,
                    label=payload.get("label", ""),
                    url=url,
                    order=order,
                )
            )
        if new_links:
            ProfileLink.objects.bulk_create(new_links)

    def create(self, validated_data):
        link_items = validated_data.pop("link_items", None)
        profile = super().create(validated_data)
        self._sync_links(profile, link_items)
        return profile

    def update(self, instance, validated_data):
        link_items = validated_data.pop("link_items", None)
        profile = super().update(instance, validated_data)
        self._sync_links(profile, link_items)
        return profile
>>>>>>> eabf36c ( migrations 수정)


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

