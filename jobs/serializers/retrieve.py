from rest_framework import serializers

from clients.models import Client
from core.models import Category
from jobs.models import Activities, Job
from proposals.models import Proposal


class JobClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["public_id", "name", "logo"]

    def to_representation(self, instance: Client):
        data = super().to_representation(instance)

        is_mini_view = "mini" in self.context

        if is_mini_view:
            return data

        data["company"] = {}
        is_detail_view = "detail" in self.context

        data["rating"] = instance.average_rating(
            recalculate=is_detail_view, db_commit=True
        )

        if not is_detail_view:
            company = instance._company
            if company:
                data["company"].update(
                    {
                        "slug": company.get("slug"),
                        "name": company.get("name"),
                        "logo_url": company.get("logo_url"),
                    }
                )
            return data

        if is_detail_view:
            data["address"] = instance.address
            data["country"] = instance.country
            company = instance.company
            if company and "detail" in self.context:
                data["company"]["slug"] = company.slug
                data["company"]["name"] = company.name
                data["company"]["logo_url"] = company.logo_url
                data["company"]["website"] = company.website
                data["company"]["industry"] = company.industry
                data["company"]["description"] = company.description
                data["company"]["date_established"] = str(
                    company.date_established or ""
                )

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
        if (
            instance.third_party_metadata
            and "description" in instance.third_party_metadata
        ):
            representation["description"] = instance.third_party_metadata["description"]
        else:
            representation["description"] = instance.description[:500]
        return representation


class JobRelatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "public_id",
            "title",
            "country",
            "address",
            "pricing",
            "application_deadline",
            "client",
        ]

    client = serializers.SerializerMethodField()

    def get_client(self, instance: Job):
        data = {
            "public_id": instance.client.public_id,
            "name": instance.client.name,
            "logo": instance.client.logo,
            "rating": instance.client.rating,
        }
        if instance.third_party_metadata:
            data["name"] = (
                instance.third_party_metadata.get("company_name") or data["name"]
            )

        return data


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
            "applicant_ids",
        ]

    category = JobCategorySerializer()
    client = JobClientSerializer(context={"detail": True})

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        representation["activities"] = JobActivitiesSerializer(
            instance=instance.get_activities
        ).data
        return representation
