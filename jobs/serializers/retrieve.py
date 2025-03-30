from rest_framework import serializers

from clients.models import Client
from core.models import Category
from jobs.models import Activities, Job
from proposals.models import Proposal


class JobClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["public_id", "name", "logo_url"]

    def to_representation(self, instance: Client):
        company = instance.company
        data = super().to_representation(instance)
        data["rating"] = instance.average_rating()

        if "detail" in self.context:
            data["address"] = instance.address
            data["country"] = instance.country

        if company:
            data["company"] = {
                "slug": company.slug,
                "name": company.name,
                "logo_url": company.logo_url,
            }
            if "detail" in self.context:
                data["company"]["website"] = company.website
                data["company"]["industry"] = company.industry
                data["company"]["description"] = company.description
                data["company"]["date_established"] = company.date_established

        return data


class JobActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activities
        fields = [
            "bits_count",
            "hired_count",
            "invite_count",
            "proposal_count",
            "interview_count",
            "unanswered_invites",
            "client_last_visit",
            "applicant_ids",
        ]

    applicant_ids = serializers.SerializerMethodField()

    def get_applicant_ids(self, instance: Activities):
        return [
            p.talent.user.public_id
            for p in Proposal.objects.only("talent__public_id").filter(job=instance.job)
        ]


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class JobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = [
            "public_id",
            "title",
            "country",
            "address",
            "category",
            "client",
            "status",
            "pricing",
            "job_type",
            "job_type_other",
            "description",
            "required_skills",
            "application_deadline",
            "created_at",
            "is_third_party",
            "third_party_metadata",
        ]

    client = JobClientSerializer()
    category = JobCategorySerializer()

    # Check if the user has proposed to the job
    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        if instance.is_third_party and "description" in instance.third_party_metadata:
            representation["description"] = instance.third_party_metadata["description"]
        else:
            representation["description"] = instance.description[:500]
        return representation


class JobRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = [
            "public_id",
            "title",
            "description",
            "pricing",
            "benefits",
            "required_skills",
            "country",
            "category",
            "address",
            "status",
            "published",
            "is_third_party",
            "third_party_address",
            "third_party_metadata",
            # Stats
            "bits_amount",
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
            "client",
            "activities",
        ]

    category = JobCategorySerializer()
    activities = JobActivitiesSerializer()
    client = JobClientSerializer(context={"detail": True})

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)

        Activities.objects.get_or_create(job=instance)

        return representation
