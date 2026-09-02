from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "full_name",
            "job_title",
            "job_title_role",
            "skills",
            "location_country",
            "location_city",
            "summary",
            "linkedin_url",
            "created_at",
            "updated_at",
        ]
