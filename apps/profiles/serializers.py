# apps/profiles/serializers.py
from rest_framework import serializers

from .models import (
    Profile, JobRole, ProfileLink,
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


class ProfileSerializer(serializers.ModelSerializer):
    job_role = JobRoleSerializer(read_only=True)
    job_role_name = serializers.CharField(source="job_role.name", read_only=True)
    job_role_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    links = ProfileLinkSerializer(many=True, read_only=True)
    link_items = ProfileLinkWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Profile
        fields = [
            "id",
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

    def validate(self, attrs):
        role_id = attrs.pop("job_role_id", None)
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
                raise serializers.ValidationError({"job_role_id": "유효한 직무가 아닙니다."})
            attrs["job_role"] = role_obj
        elif "job_role" in attrs and attrs["job_role"] is None:
            attrs["job_role"] = None
        return attrs

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
