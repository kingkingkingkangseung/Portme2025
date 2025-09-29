from rest_framework import generics, permissions, viewsets
from django.shortcuts import get_object_or_404
from .models import (
    Activity, ActivityMemo, ActivityCategory, Tag,
    Award, Certification, ForeignLang, GlobalExp
)
from .serializers import (
    ActivitySerializer, ActivityMemoSerializer, ActivityCategorySerializer, TagSerializer,
    AwardSerializer, CertificationSerializer, ForeignLangSerializer, GlobalExpSerializer
)

# ===== Activity =====
class ActivityListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Activity, pk=self.kwargs["pk"], user=self.request.user)


# ===== Award / Certification / GlobalExp / ForeignLang =====
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


class ForeignLangViewSet(viewsets.ModelViewSet):
    serializer_class = ForeignLangSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ForeignLang.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GlobalExpViewSet(viewsets.ModelViewSet):
    serializer_class = GlobalExpSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GlobalExp.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
