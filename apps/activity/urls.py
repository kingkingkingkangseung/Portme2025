from django.urls import path
from .views import (
    ActivityListCreateAPIView, ActivityDetailAPIView,
    ActivityMemoListCreateAPIView, ActivityMemoDetailAPIView,
)

urlpatterns = [
    path("",                ActivityListCreateAPIView.as_view(), name="activity-list"),
    path("<int:pk>/",       ActivityDetailAPIView.as_view(),     name="activity-detail"),

    # 메모
    path("<int:activity_id>/memos/",          ActivityMemoListCreateAPIView.as_view(), name="activity-memo-list"),
    path("<int:activity_id>/memos/<int:pk>/", ActivityMemoDetailAPIView.as_view(),     name="activity-memo-detail"),
]
