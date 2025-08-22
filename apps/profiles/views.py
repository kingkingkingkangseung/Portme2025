# apps/profiles/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from .models import Profile, JobRole
from .serializers import ProfileSerializer, JobRoleSerializer

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

class LevelListAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        data = [{"value": v, "label": l} for v, l in Profile.Level.choices]
        return Response(data)
