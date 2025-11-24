# apps/profiles/serializers.py
from rest_framework import serializers

from .models import (
    Profile, JobRole, ProfileLink, ProfileMajor,
    JobCategory, HardSkill, SoftSkill,
    JobHardSkill, JobSoftSkill,
)


class JobRoleSerializer(serializers.ModelSerializer):
    job_category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JobRole
        fields = ("id", "name", "group", "job_category")

    def get_job_category(self, obj):
        if not obj.job_category:
            return None
        return {"id": obj.job_category.id, "name": obj.job_category.name}


class ProfileLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileLink
        fields = ("id", "label", "url", "order")


class ProfileLinkWriteSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=50, required=False, allow_blank=True)
    url = serializers.URLField()
    order = serializers.IntegerField(required=False, min_value=0)


class ProfileMajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileMajor
        fields = ("id", "major_type", "major_name", "order")


class ProfileMajorWriteSerializer(serializers.Serializer):
    major_type = serializers.CharField(max_length=20, required=False, allow_blank=True)
    major_name = serializers.CharField(max_length=120)
    order = serializers.IntegerField(required=False, min_value=0)


DATE_INPUT_FORMATS = ["%Y-%m-%d", "%Y.%m.%d", "%Y-%m", "%Y.%m"]


class OptionalDateField(serializers.DateField):
    def to_internal_value(self, value):
        if value in ("", None):
            return None
        return super().to_internal_value(value)


class ProfileSerializer(serializers.ModelSerializer):
    links = ProfileLinkSerializer(many=True, read_only=True)
    link_items = ProfileLinkWriteSerializer(many=True, write_only=True, required=False)
    majors = ProfileMajorSerializer(many=True, read_only=True)
    major_items = ProfileMajorWriteSerializer(many=True, write_only=True, required=False)
    birth_date = OptionalDateField(
        required=False,
        allow_null=True,
        input_formats=DATE_INPUT_FORMATS[:2],
    )
    admission_date = OptionalDateField(
        required=False,
        allow_null=True,
        input_formats=DATE_INPUT_FORMATS,
    )
    graduation_date = OptionalDateField(
        required=False,
        allow_null=True,
        input_formats=DATE_INPUT_FORMATS,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "full_name", "bio", "avatar",
            "birth_date", "phone_number", "contact_email",
            "school_name", "admission_date", "graduation_date",
            "graduation_status", "gpa", "gpa_total",
            "job_role_name",
            "links", "link_items",
            "majors", "major_items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "links", "majors"]
        extra_kwargs = {
            "contact_email": {"allow_blank": True, "required": False},
            "phone_number": {"allow_blank": True, "required": False},
            "full_name": {"required": False},
            "bio": {"required": False},
            "job_role_name": {"allow_blank": True, "required": False},
            "graduation_status": {"allow_blank": True, "required": False},
            "gpa": {"required": False, "allow_null": True},
            "gpa_total": {"required": False, "allow_null": True},
        }

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

    def _sync_majors(self, profile: Profile, major_items):
        if major_items is None:
            return
        profile.majors.all().delete()
        bulk = []
        for idx, payload in enumerate(major_items):
            name = payload.get("major_name")
            if not name:
                continue
            order = payload.get("order")
            if order is None:
                order = idx
            bulk.append(
                ProfileMajor(
                    profile=profile,
                    major_type=payload.get("major_type", ""),
                    major_name=name,
                    order=order,
                )
            )
        if bulk:
            ProfileMajor.objects.bulk_create(bulk)

    def create(self, validated_data):
        link_items = validated_data.pop("link_items", None)
        major_items = validated_data.pop("major_items", None)
        profile = super().create(validated_data)
        self._sync_links(profile, link_items)
        self._sync_majors(profile, major_items)
        return profile

    def update(self, instance, validated_data):
        link_items = validated_data.pop("link_items", None)
        major_items = validated_data.pop("major_items", None)
        profile = super().update(instance, validated_data)
        self._sync_links(profile, link_items)
        self._sync_majors(profile, major_items)
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
