from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id", "display_name", "bio", "avatar", "website",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
