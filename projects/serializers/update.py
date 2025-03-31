from rest_framework import serializers

from projects.models import Project, ProjectStatusChoices


class ProjectStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=ProjectStatusChoices.choices, required=True
    )

    class Meta:
        model = Project
        fields = [
            "status",
            "rejection_comment",
            "acceptance_comment",
            "completion_comment",
            "termination_comment",
            "cancellation_comment",
        ]

    def validate(self, attrs):
        if attrs.get("status") == ProjectStatusChoices.REJECTED.value and not attrs.get(
            "rejection_comment"
        ):
            raise serializers.ValidationError(
                "rejection_comment is required", "comment"
            )
        if attrs.get("status") == ProjectStatusChoices.ACCEPTED.value and not attrs.get(
            "acceptance_comment"
        ):
            raise serializers.ValidationError(
                "acceptance_comment is required", "comment"
            )

        if attrs.get(
            "status"
        ) == ProjectStatusChoices.TERMINATED.value and not attrs.get(
            "termination_comment"
        ):
            raise serializers.ValidationError(
                "termination_comment is required", "comment"
            )

        if attrs.get(
            "status"
        ) == ProjectStatusChoices.CANCELLED.value and not attrs.get(
            "cancellation_comment"
        ):
            raise serializers.ValidationError(
                "cancellation_comment is required", "comment"
            )

        return super().validate(attrs)
