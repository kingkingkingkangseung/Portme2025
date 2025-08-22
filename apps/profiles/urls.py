# apps/profiles/urls.py
from django.urls import path
from .views import MyProfileAPIView, JobRoleListAPIView, LevelListAPIView

urlpatterns = [
    path('me/', MyProfileAPIView.as_view(), name='my-profile'),
    path('options/job-roles/', JobRoleListAPIView.as_view(), name='job-role-list'),
    path('options/levels/', LevelListAPIView.as_view(), name='level-list'),
]
