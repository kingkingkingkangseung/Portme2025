from rest_framework import serializers
from .models import Activity, ActivityMemo

class ActivityMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMemo
        fields = ["id", "content", "date"]
        read_only_fields = ["id", "date"]

class ActivitySerializer(serializers.ModelSerializer):
    memos = ActivityMemoSerializer(many=True, read_only=True)  # 읽기용으로 메모 포함

    class Meta:
        model = Activity
        fields = [
            "id",
            "title", "period_start", "period_end",
            "role", "description", "outcome",
            "attachment",
            "created_at", "updated_at",
            "memos",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "memos"]
