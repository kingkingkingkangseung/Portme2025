from rest_framework import generics, permissions
from .models import Activity, ActivityMemo
from .serializers import ActivitySerializer, ActivityMemoSerializer

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
