from django.urls import path
from .views import ActivityListCreateAPIView, ActivityDetailAPIView

urlpatterns = [
    path('',     ActivityListCreateAPIView.as_view(), name='activity-list'),
    path('<int:pk>/', ActivityDetailAPIView.as_view(), name='activity-detail'),
]