from django.apps import apps  # ⬅️ 추가
from rest_framework import generics, permissions
from .models import Activity, ActivityMemo, ActivityCategory, Tag
from .serializers import (
    ActivitySerializer, ActivityMemoSerializer,
    ActivityCategorySerializer, TagSerializer,
)

class ActivityListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/activities/      → 내 활동 목록
    POST /api/activities/      → 활동 생성
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/activities/{pk}/
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return generics.get_object_or_404(
            Activity, pk=self.kwargs["pk"], user=self.request.user
        )


# ------- 메모 API -------
class ActivityMemoListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/activities/{activity_id}/memos/
    POST /api/activities/{activity_id}/memos/
    """
    serializer_class = ActivityMemoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_activity(self):
        return generics.get_object_or_404(
            Activity, pk=self.kwargs["activity_id"], user=self.request.user
        )

    def get_queryset(self):
        return ActivityMemo.objects.filter(activity=self.get_activity())

    def perform_create(self, serializer):
        serializer.save(activity=self.get_activity())


class ActivityMemoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/activities/{activity_id}/memos/{pk}/
    """
    serializer_class = ActivityMemoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        activity = generics.get_object_or_404(
            Activity, pk=self.kwargs["activity_id"], user=self.request.user
        )
        return generics.get_object_or_404(
            ActivityMemo, pk=self.kwargs["pk"], activity=activity
        )


# ------- 카테고리/태그 공개 목록(드롭다운 용) -------
class ActivityCategoryListAPIView(generics.ListAPIView):
    queryset = ActivityCategory.objects.filter(is_active=True).order_by("order")
    serializer_class = ActivityCategorySerializer
    permission_classes = [permissions.AllowAny]   # 로그인 없이 조회 가능


class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Tag.objects.all().order_by("name")
        kind = self.request.query_params.get("kind")
        return qs.filter(kind=kind) if kind in ("soft", "hard") else qs


# ------- (선택) 활동별 회고 목록 엔드포인트 -------
class ActivityRetrosAPIView(generics.ListAPIView):
    """
    GET /api/activities/{pk}/retros/  → 이 활동에 연결된 회고 리스트
    """
    permission_classes = [permissions.IsAuthenticated]

    # 간단 Serializer를 즉석에서 사용 (모델 import 없이도 동작)
    class _RetroMiniSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        created_at = serializers.DateTimeField()

    serializer_class = _RetroMiniSerializer

    def get_queryset(self):
        activity = generics.get_object_or_404(
            Activity, pk=self.kwargs["pk"], user=self.request.user
        )
        Post = apps.get_model("community", "Post")
        return (Post.objects
                .filter(type="retro", activities=activity, user=self.request.user)
                .order_by("-created_at"))
