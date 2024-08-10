from rest_framework import serializers
from jobs.models import Job


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "budget",
            "activities_id",
            "required_skills",
            "location",
        ]
