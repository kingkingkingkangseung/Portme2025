from django.urls import path
from .views import (
    ActivityListCreateAPIView, ActivityDetailAPIView,
    ActivityCategoryListAPIView, TagListAPIView,
)

urlpatterns = [
    # Activity 기본 CRUD
    path("",          ActivityListCreateAPIView.as_view(), name="activity-list"),
    path("<int:pk>/", ActivityDetailAPIView.as_view(),     name="activity-detail"),

    # 카테고리/태그
    path("categories/", ActivityCategoryListAPIView.as_view(), name="activity-category-list"),
    path("tags/",       TagListAPIView.as_view(),             name="tag-list"),
]
