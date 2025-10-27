from django.urls import path
from .views import (
    ActivityListCreateAPIView, ActivityDetailAPIView,
    ActivityMemoListCreateAPIView, ActivityMemoDetailAPIView,
    ActivityCategoryListAPIView, TagListAPIView,
    ActivityHardSkillListCreateAPIView, ActivityHardSkillDetailAPIView,
    ActivitySoftSkillListCreateAPIView, ActivitySoftSkillDetailAPIView,
)

urlpatterns = [
    path("", ActivityListCreateAPIView.as_view(), name="activity-list"),
    path("<int:pk>/", ActivityDetailAPIView.as_view(), name="activity-detail"),

    # 메모
    path("<int:activity_id>/memos/", ActivityMemoListCreateAPIView.as_view(), name="activity-memo-list"),
    path("<int:activity_id>/memos/<int:pk>/", ActivityMemoDetailAPIView.as_view(), name="activity-memo-detail"),

    # 카테고리/태그
    path("categories/", ActivityCategoryListAPIView.as_view(), name="activity-category-list"),
    path("tags/", TagListAPIView.as_view(), name="tag-list"),
    # 스킬 링크
    path("<int:activity_id>/hard-skills/", ActivityHardSkillListCreateAPIView.as_view(), name="activity-hard-skill-list"),
    path("<int:activity_id>/hard-skills/<int:pk>/", ActivityHardSkillDetailAPIView.as_view(), name="activity-hard-skill-detail"),
    path("<int:activity_id>/soft-skills/", ActivitySoftSkillListCreateAPIView.as_view(), name="activity-soft-skill-list"),
    path("<int:activity_id>/soft-skills/<int:pk>/", ActivitySoftSkillDetailAPIView.as_view(), name="activity-soft-skill-detail"),
]
