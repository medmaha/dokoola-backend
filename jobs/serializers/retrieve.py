from rest_framework import serializers

from jobs.serializers.utils import check_has_proposed

from clients.serializer import (
    ClientDetailSerializer,
)

from jobs.models import Job, Pricing

from .others import PricingSerializer


class JobMiniSerializer(serializers.ModelSerializer):
    pricing = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "slug",
            "title",
            "client",
            "budget",
            "status",
            "pricing",
            "published",
            "description",
            "created_at",
        ]

    def get_client(self, instance: Job):
        return {
            "name": instance.client.user.name,
            "avatar": instance.client.user.avatar,
            "username": instance.client.user.username,
            "rating": instance.client.calculate_rating(),
        }

    def get_pricing(self, instance: Job):
        return PricingSerializer(instance.pricing).data


class JobListSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    has_proposed = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "slug",
            "title",
            "client",
            "budget",
            "category",
            "location",
            "duration",
            "required_skills",
            "status",
            "published",
            "has_proposed",
            "description",
            "payment_type",
            "updated_at",
            "created_at",
        ]

    # Check if the user has proposed to the job
    def get_has_proposed(self, instance: Job):
        return check_has_proposed(self.context, instance)

    def get_client(self, instance: Job):
        return {
            "name": instance.client.user.name,
            "avatar": instance.client.user.avatar,
            "username": instance.client.user.username,
            "rating": instance.client.calculate_rating(),
            "bio": instance.client.bio[:100],
            "location": instance.client.user.get_location(),
            "country": instance.client.user.country,
        }

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        description = representation.get("description", "")
        representation.update({"description": description[:200]})
        representation["proposal_count"] = instance.activities.proposal_count

        return representation


class MyJobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "slug",
            "title",
            "client",
            "budget",
            "category",
            "location",
            "duration",
            "required_skills",
            "status",
            "published",
            "payment_type",
            "updated_at",
            "created_at",
        ]

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        representation["proposals_count"] = instance.activities.proposal_count
        return representation


class JobRetrieveSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    pricing = PricingSerializer()
    has_proposed = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "slug",
            "title",
            "client",
            "budget",
            "pricing",
            "category",
            "location",
            "duration",
            "created_at",
            "activities",
            "has_proposed",
            "status",
            "published",
            "description",
            "required_skills",
        ]

    def get_has_proposed(self, instance: Job):
        return check_has_proposed(self.context, instance)

    def get_client(self, instance: Job):
        return {
            "name": instance.client.user.name,
            "avatar": instance.client.user.avatar,
            "username": instance.client.user.username,
            "rating": instance.client.calculate_rating(),
            "bio": instance.client.bio[:100],
            "location": instance.client.user.get_location(),
            "country": instance.client.user.country,
        }
