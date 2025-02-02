from django.db.models import Count
from rest_framework import serializers

from jobs.models import Activities, Job


class JobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "country",
            "address",
            "client",
            "status",
            "pricing",
            "job_type",
            "job_type_other",
            "description",
            "required_skills",
            "is_third_party",
            "application_deadline",
            "created_at",
        ]

    # Check if the user has proposed to the job
    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        representation["proposal_count"] = instance.proposal_count
        representation["description"] = instance.description[:200]
        representation["category"] = {
            "slug": instance.category.slug,
            "name": instance.category.name,
        }
        representation["client"] = {
            "id": instance.client.id,
            # "username": instance.client.user.username,
            "name": instance.client.name,
            "company": (
                {
                    "slug": instance.client.company.slug,
                    "name": instance.client.company.name,
                    "logo_url": instance.client.company.logo_url,
                }
                if instance.client.company
                else None
            ),
        }

        return representation


class JobRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "pricing",
            "benefits",
            "required_skills",
            "country",
            "address",
            "category",
            "status",
            "published",
            "is_third_party",
            "third_party_address",
            # Stats
            "bits_amount",
            "views_count",
            "proposal_count",
            "invitation_count",
            "client_last_visit",
            # # Stats
            "job_type",
            "job_type_other",
            "experience_level",
            "experience_level_other",
            # 
            "estimated_duration",
            "application_deadline",
            "additional_payment_terms",
            # 
            "client",
            "updated_at",
            "created_at",
        ]

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        representation["category"] = {
            "slug": instance.category.slug,
            "name": instance.category.name,
        }
        representation["client"] = {
            "id": instance.client.id,
            "name": instance.client.name,
            "username": instance.client.user.username,
            "avatar": instance.client.user.avatar,
            "company": (
                {
                    "slug": instance.client.company.slug,
                    "name": instance.client.company.name,
                    "logo_url": instance.client.company.logo_url,
                }
                if instance.client.company
                else None
            ),
        }

        activity = Activities.objects.select_related().filter(job=instance)

        representation["activities"] = (
            activity.values(
                "bits_count",
                "hired_count",
                "invite_count",
                "proposal_count",
                "interview_count",
                "unanswered_invites",
                "client_last_visit",
            ).first()
            if activity
            else None
        )

        if activity:
            representation["activities"]["hired"] = []

        return representation
