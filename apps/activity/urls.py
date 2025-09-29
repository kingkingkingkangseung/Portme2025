from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityListCreateAPIView, ActivityDetailAPIView,
    ActivityMemoListCreateAPIView, ActivityMemoDetailAPIView,
    ActivityCategoryListAPIView, TagListAPIView,
    AwardViewSet, CertificationViewSet,
)

router = DefaultRouter()
router.register(r"awards", AwardViewSet, basename="award")
router.register(r"certifications", CertificationViewSet, basename="certification")

urlpatterns = [
    path("",                ActivityListCreateAPIView.as_view(), name="activity-list"),
    path("<int:pk>/",       ActivityDetailAPIView.as_view(),     name="activity-detail"),

    # 메모
    path("<int:activity_id>/memos/",          ActivityMemoListCreateAPIView.as_view(), name="activity-memo-list"),
    path("<int:activity_id>/memos/<int:pk>/", ActivityMemoDetailAPIView.as_view(),     name="activity-memo-detail"),

    # 카테고리/태그
    path("categories/", ActivityCategoryListAPIView.as_view(), name="activity-category-list"),
    path("tags/",       TagListAPIView.as_view(),             name="tag-list"),

    # Award / Certification
    path("", include(router.urls)),
]
