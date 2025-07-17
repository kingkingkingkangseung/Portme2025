from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Portfolio
from .serializers import PortfolioSerializer, PortfolioDetailSerializer
from apps.activity.models import Activity

class PortfolioListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PortfolioDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            Portfolio,
            pk=self.kwargs['pk'],
            user=self.request.user
        )


class PortfolioAddActivityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        activity_id = request.data.get('activity_id')
        if not activity_id:
            return Response(
                {'activity_id': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        activity = get_object_or_404(Activity, pk=activity_id, user=request.user)
        portfolio.activities.add(activity)
        return Response({
            'portfolio_id': portfolio.id,
            'activity_id': activity.id
        })


class PortfolioRemoveActivityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
        activity_id = request.data.get('activity_id')
        if not activity_id:
            return Response(
                {'activity_id': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        activity = get_object_or_404(Activity, pk=activity_id, user=request.user)
        portfolio.activities.remove(activity)
        return Response(status=status.HTTP_204_NO_CONTENT)
