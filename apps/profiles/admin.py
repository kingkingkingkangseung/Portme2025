# apps/profiles/admin.py
from django.contrib import admin
from .models import Profile, JobRole

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group", "order", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("name",)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "job_role", "level", "updated_at")
    list_filter = ("level", "job_role")
    search_fields = ("user__username", "full_name")
