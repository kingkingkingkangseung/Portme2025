from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Portfolio, Project, ProjectCategory
from .serializers import (
    PortfolioSerializer, PortfolioDetailSerializer,
    ProjectSerializer, ProjectCategorySerializer,
)
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


# ---------- ERD 확장: 프로젝트 ----------

class ProjectCategoryListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProjectCategorySerializer
    queryset = ProjectCategory.objects.filter(is_active=True).order_by('order', 'code')


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['pk'], user=self.request.user)


class ProjectAddActivityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        activity_id = request.data.get('activity_id')
        if not activity_id:
            return Response({'activity_id': ['This field is required.']}, status=400)
        activity = get_object_or_404(Activity, pk=activity_id, user=request.user)
        project.activities.add(activity)
        return Response({'project_id': project.id, 'activity_id': activity.id})


class ProjectRemoveActivityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        activity_id = request.data.get('activity_id')
        if not activity_id:
            return Response({'activity_id': ['This field is required.']}, status=400)
        activity = get_object_or_404(Activity, pk=activity_id, user=request.user)
        project.activities.remove(activity)
        return Response(status=204)
