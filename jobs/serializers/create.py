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
            "job_type_other",
            "description",
            "required_skills",
            "estimated_duration",
            "third_party_address",
            "application_deadline",
            "experience_level",
            "experience_level_other",
        ]
