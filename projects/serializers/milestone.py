from django.db import models
from rest_framework import serializers
from projects.models import Milestone
from .acknowledgement import AcknowledgementRetrieveSerializer


class MilestoneRetrieveSerializer(serializers.ModelSerializer):
    acknowledgement = AcknowledgementRetrieveSerializer()

    class Meta:
        model = Milestone
        fields = (
            "id",
            "status",
            "milestone_name",
            "milestone_description",
            "acknowledgement",
            "created_at",
            "updated_at",
            "published",
            "is_final",
            "due_date",
            "project_pk",
        )


class MilestoneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = (
            "status",
            "milestone_name",
            "milestone_description",
            "published",
            "due_date",
        )


class MilestoneUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = (
            "status",
            "milestone_name",
            "milestone_description",
            "published",
            "due_date",
        )
