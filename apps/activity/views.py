from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from .models import (
    Activity,
    ActivityMemo,
    ActivityCategory,
    Tag,
    Career,
    Award,
    Certification,
    GlobalExp,
    ForeignLang,
    ActivityHardSkill,
    ActivitySoftSkill,
    SubActivity,
)
from .serializers import (
    ActivitySerializer,
    ActivityMemoSerializer,
    ActivityCategorySerializer,
    TagSerializer,
    CareerSerializer,
    AwardSerializer,
    CertificationSerializer,
    GlobalExpSerializer,
    ForeignLangSerializer,
    ActivityHardSkillSerializer,
    ActivitySoftSkillSerializer,
    SubActivitySerializer,
)

# -------- 활동 CRUD --------
class ActivityListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Activity.objects.filter(user=self.request.user, is_deleted=False).order_by("-updated_at")

        category_id = self.request.query_params.get("category_id")
        category_key = self.request.query_params.get("category")
        status_param = self.request.query_params.get("status")

        if category_id:
            qs = qs.filter(category_id=category_id)
        if category_key:
            qs = qs.filter(category__key=category_key)
        if status_param:
            qs = qs.filter(status=status_param)

        return qs

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


# -------- Award / Certification / Career / GlobalExp / ForeignLang --------
class CareerViewSet(viewsets.ModelViewSet):
    serializer_class = CareerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Career.objects.filter(user=self.request.user)
        employment_type = self.request.query_params.get("employment_type")
        if employment_type:
            qs = qs.filter(employment_type=employment_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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


class GlobalExpViewSet(viewsets.ModelViewSet):
    serializer_class = GlobalExpSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GlobalExp.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ForeignLangViewSet(viewsets.ModelViewSet):
    serializer_class = ForeignLangSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ForeignLang.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------- ERD 확장: Activity ↔ Skill --------
class ActivityHardSkillListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ActivityHardSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_activity(self):
        return get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)

    def get_queryset(self):
        return ActivityHardSkill.objects.filter(activity=self.get_activity()).order_by("id")

    def perform_create(self, serializer):
        serializer.save(activity=self.get_activity())


class ActivityHardSkillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivityHardSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        activity = get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)
        return get_object_or_404(ActivityHardSkill, pk=self.kwargs["pk"], activity=activity)


class ActivitySoftSkillListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ActivitySoftSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_activity(self):
        return get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)

    def get_queryset(self):
        return ActivitySoftSkill.objects.filter(activity=self.get_activity()).order_by("id")

    def perform_create(self, serializer):
        serializer.save(activity=self.get_activity())


class ActivitySoftSkillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivitySoftSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        activity = get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)
        return get_object_or_404(ActivitySoftSkill, pk=self.kwargs["pk"], activity=activity)


# -------- 포함된 활동(세부 활동) --------
class SubActivityListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SubActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_activity(self):
        return get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)

    def get_queryset(self):
        return SubActivity.objects.filter(activity=self.get_activity()).order_by("period_start", "id")

    def perform_create(self, serializer):
        serializer.save(activity=self.get_activity())


class SubActivityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        activity = get_object_or_404(Activity, pk=self.kwargs["activity_id"], user=self.request.user)
        return get_object_or_404(activity.sub_activities, pk=self.kwargs["pk"])
