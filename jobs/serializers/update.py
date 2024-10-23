from rest_framework import serializers

from jobs.models import Job


class JobUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "title",
            "budget",
            "location",
            "published",
            "description",
            "required_skills",
        ]
