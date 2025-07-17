from rest_framework import serializers
from .models import Activity

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            'id', 'summary', 'role', 'field', 'date',
            'skills',
            'role_detail', 'process_detail', 'learn_detail', 'result_detail',
            'thumbnail',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']