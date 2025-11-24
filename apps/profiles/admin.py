# apps/profiles/admin.py
from django.contrib import admin
from .models import Profile, JobRole, ProfileLink

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group", "order", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("name",)

class ProfileLinkInline(admin.TabularInline):
    model = ProfileLink
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "job_role", "phone_number", "updated_at")
    list_filter = ("job_role",)
    search_fields = ("user__username", "full_name", "phone_number")
    inlines = [ProfileLinkInline]


@admin.register(ProfileLink)
class ProfileLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "label", "url", "order")
    list_filter = ("profile",)
    search_fields = ("label", "url")
