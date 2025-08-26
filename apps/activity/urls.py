from django.urls import path
from .views import (
    ActivityListCreateAPIView, ActivityDetailAPIView,
    ActivityMemoListCreateAPIView, ActivityMemoDetailAPIView,
    ActivityCategoryListAPIView, TagListAPIView,
    ActivityRetrosAPIView,  
)

urlpatterns = [
    path("",                ActivityListCreateAPIView.as_view(), name="activity-list"),
    path("<int:pk>/",       ActivityDetailAPIView.as_view(),     name="activity-detail"),
    path("<int:pk>/retros/", ActivityRetrosAPIView.as_view(),    name="activity-retros"),

    # 메모
    path("<int:activity_id>/memos/",          ActivityMemoListCreateAPIView.as_view(), name="activity-memo-list"),
    path("<int:activity_id>/memos/<int:pk>/", ActivityMemoDetailAPIView.as_view(),     name="activity-memo-detail"),

    # 카테고리/태그
    path("categories/", ActivityCategoryListAPIView.as_view(), name="activity-category-list"),
    path("tags/",       TagListAPIView.as_view(),             name="tag-list"),
]
