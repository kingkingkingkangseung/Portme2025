# apps/profiles/urls.py
from django.urls import path
from .views import (
    MyProfileAPIView, JobRoleListAPIView, LevelListAPIView,
    JobCategoryListAPIView, HardSkillListAPIView, SoftSkillListAPIView,
    JobRoleSkillsAPIView,
)

urlpatterns = [
    path('me/', MyProfileAPIView.as_view(), name='my-profile'),
    path('options/job-roles/', JobRoleListAPIView.as_view(), name='job-role-list'),
    path('options/levels/', LevelListAPIView.as_view(), name='level-list'),
    # ERD 확장: 직무/스킬
    path('options/job-categories/', JobCategoryListAPIView.as_view(), name='job-category-list'),
    path('options/hard-skills/', HardSkillListAPIView.as_view(), name='hard-skill-list'),
    path('options/soft-skills/', SoftSkillListAPIView.as_view(), name='soft-skill-list'),
    path('job-roles/<int:role_id>/skills/', JobRoleSkillsAPIView.as_view(), name='job-role-skills'),
]
