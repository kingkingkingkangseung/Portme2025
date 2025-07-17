from rest_framework import generics, permissions
from .models import Activity
from .serializers import ActivitySerializer

class ActivityListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/activities/    → 내 활동 목록 조회
    POST /api/activities/    → 새 활동 생성
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 로그인한 유저의 활동만 반환
        return Activity.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        # 생성 시 user 필드 자동 저장
        serializer.save(user=self.request.user)


class ActivityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/activities/{pk}/   → 활동 상세 조회
    PUT    /api/activities/{pk}/   → 활동 전체 수정
    PATCH  /api/activities/{pk}/   → 활동 부분 수정
    DELETE /api/activities/{pk}/   → 활동 삭제
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # 본인 활동만 조회/수정/삭제 허용
        return generics.get_object_or_404(
            Activity, pk=self.kwargs['pk'], user=self.request.user
        )