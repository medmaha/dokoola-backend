from rest_framework import serializers
from jobs.models import Job


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "title",
            "country",
            "address",
            "pricing",
            "benefits",
            "job_type",
            "description",
            "required_skills",
            "experience_level",
            "estimated_duration",
            "third_party_address",
            "application_deadline",
            "job_type_other",
            "experience_level_other",
        ]
