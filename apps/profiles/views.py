# apps/profiles/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.shortcuts import get_object_or_404
from .models import (
    Profile, JobRole,
    JobCategory, HardSkill, SoftSkill,
    JobHardSkill, JobSoftSkill,
)
from .serializers import (
    ProfileSerializer, JobRoleSerializer,
    JobCategorySerializer, HardSkillSerializer, SoftSkillSerializer,
    JobRoleSkillsSerializer, JobRoleSkillsUpdateSerializer,
)

class MyProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(profile).data)

    def put(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        ser = ProfileSerializer(instance=profile, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        ser = ProfileSerializer(instance=profile, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

# 드롭다운 옵션
class JobRoleListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = JobRoleSerializer

    def get_queryset(self):
        qs = JobRole.objects.filter(is_active=True)
        group = self.request.query_params.get("group")  # dev/design/pm/biz/etc
        return qs.filter(group=group).order_by("order", "name") if group else qs


# ---------- ERD 확장: 직무/스킬 ----------

class JobCategoryListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = JobCategorySerializer
    queryset = JobCategory.objects.filter(is_active=True).order_by("order", "name")


class HardSkillListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = HardSkillSerializer

    def get_queryset(self):
        qs = HardSkill.objects.all().order_by("name")
        q = self.request.query_params.get("q")
        code = self.request.query_params.get("code")
        if q:
            qs = qs.filter(name__icontains=q)
        if code:
            qs = qs.filter(code__icontains=code)
        return qs


class SoftSkillListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SoftSkillSerializer

    def get_queryset(self):
        qs = SoftSkill.objects.all().order_by("name")
        q = self.request.query_params.get("q")
        return qs.filter(name__icontains=q) if q else qs


class JobRoleSkillsAPIView(APIView):
    """GET: 직무의 하드/소프트 스킬 목록
       POST: 직무-스킬 매핑 저장(덮어쓰기)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, role_id: int):
        role = get_object_or_404(JobRole, pk=role_id, is_active=True)
        hard = HardSkill.objects.filter(jobhardskill__job_role=role).order_by("name")
        soft = SoftSkill.objects.filter(jobsoftskill__job_role=role).order_by("name")
        payload = JobRoleSkillsSerializer({
            "job_role": role,
            "hard_skills": hard,
            "soft_skills": soft,
        }).data
        return Response(payload)

    def post(self, request, role_id: int):
        role = get_object_or_404(JobRole, pk=role_id, is_active=True)
        ser = JobRoleSkillsUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        hard_ids = ser.validated_data.get("hard_ids", None)
        soft_ids = ser.validated_data.get("soft_ids", None)

        if hard_ids is not None:
            JobHardSkill.objects.filter(job_role=role).delete()
            JobHardSkill.objects.bulk_create([
                JobHardSkill(job_role=role, hard_skill_id=i) for i in hard_ids
            ])
        if soft_ids is not None:
            JobSoftSkill.objects.filter(job_role=role).delete()
            JobSoftSkill.objects.bulk_create([
                JobSoftSkill(job_role=role, soft_skill_id=i) for i in soft_ids
            ])

        return self.get(request, role_id)
