from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from .models import (
    Activity, ActivityMemo, ActivityCategory, Tag, Award, Certification
)
from .serializers import (
    ActivitySerializer, ActivityMemoSerializer, ActivityCategorySerializer, TagSerializer,
    AwardSerializer, CertificationSerializer
)


# -------- 활동 CRUD --------
class ActivityListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Activity, pk=self.kwargs["pk"], user=self.request.user)


# -------- 메모 --------
class ActivityMemoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ActivityMemoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_activity(self):
        return get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)

    def get_queryset(self):
        return self.get_activity().memos.all()

    def perform_create(self, serializer):
        serializer.save(activity=self.get_activity())


class ActivityMemoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivityMemoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        activity = get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)
        return get_object_or_404(activity.memos, pk=self.kwargs["pk"])


# -------- 카테고리/태그 --------
class ActivityCategoryListAPIView(generics.ListAPIView):
    queryset = ActivityCategory.objects.filter(is_active=True).order_by("order")
    serializer_class = ActivityCategorySerializer
    permission_classes = [permissions.AllowAny]


class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Tag.objects.all().order_by("name")
        kind = self.request.query_params.get("kind")
        q = self.request.query_params.get("q")

        if kind in ("soft", "hard", "job"):
            qs = qs.filter(kind=kind)
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


# -------- Award / Certification --------
class AwardViewSet(viewsets.ModelViewSet):
    serializer_class = AwardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Award.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CertificationViewSet(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
