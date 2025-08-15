from django.contrib import admin
from .models import Activity, ActivityMemo

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "period_start", "period_end", "updated_at")
    list_filter = ("user",)
    search_fields = ("title", "user__username")

@admin.register(ActivityMemo)
class ActivityMemoAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "date")
    search_fields = ("activity__title",)
