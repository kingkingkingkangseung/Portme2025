from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Profile
from .serializers import ProfileSerializer


class MyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]  # JWT 인증된 유저만 접근 가능
    
    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({"detail": "프로필이 존재하지 않습니다."}, status=404)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)