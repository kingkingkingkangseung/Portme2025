from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status           # ① status 임포트 추가

from .models import Profile
from .serializers import ProfileSerializer

class MyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]  # JWT 인증된 유저만 접근 가능
    
    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"detail": "프로필이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):                   # ② PUT 메서드 추가
        # (1) 프로필이 있으면 가져오고, 없으면 새로 생성
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # (2) 기존 instance(profile)에다가 request.data로 덮어쓰기
        serializer = ProfileSerializer(
            instance=profile,
            data=request.data,
        )
        
        # (3) 유효성 검사 & 저장
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # (4) 에러 응답
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):                   # ← 여기 추가
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(
            instance=profile,
            data=request.data,
            partial=True                       # ← 부분 업데이트 허용
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
