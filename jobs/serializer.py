from rest_framework import serializers

from users.serializer import User
from clients.serializer import (
    ClientSerializer,
    ClientDetailSerializer,
    ClientUpdateDataSerializer,
)
from proposals.models import Proposal

from .models import Job, Pricing, Activities


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = "__all__"


class JobsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "budget",
            "activities_id",
            "required_skills",
            "location",
            "category",
        ]


class JobMiniSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    pricing = Pricing()

    class Meta:
        model = Job
        fields = [
            "id",
            "slug",
            "title",
            "client",
            "budget",
            "pricing",
            "active_state",
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


class JobsSerializer(serializers.ModelSerializer):
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
            "bits_count",
            "active_state",
            "has_proposed",
            "description",
            "payment_type",
            "updated_at",
            "created_at",
        ]

        # Check if the user has proposed to the job

    # Check if the user has proposed to the job
    def get_has_proposed(self, instance: Job):
        request = self.context.get("request")
        user: User | None = request.user if request else None

        # Check if the request user is authenticated
        if user and user.is_authenticated:

            # Retrieve the user profile information
            [freelancer, profile_name] = user.profile

            # Check if the user is a freelancer
            if profile_name.lower() == "freelancer":

                # Check if the user has proposed to the job
                has_proposed = (
                    Proposal.objects.select_related()
                    .filter(job=instance, freelancer=freelancer)
                    .exists()
                )

                # return a boolean value
                return has_proposed

        return False

    # Update the category and required-skills data to a list of strings
    def update_categories_and_skills(self, data):
        try:
            data.update(
                {
                    "category": data.get("category", "").split(","),
                    "required_skills": data.get("required_skills", "").split(","),
                }
            )
            return data
        except KeyError:
            pass
        return data

    def get_client(self, instance: Job):
        return {
            "name": instance.client.user.name,
            "avatar": instance.client.user.avatar,
            "username": instance.client.user.username,
            "rating": instance.client.calculate_rating(),
        }

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        data = self.update_categories_and_skills(representation)
        description = representation.get("description", "")
        data.update({"description": description[:200]})

        return data


class JobsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "title",
            "budget",
            "category",
            "location",
            "active_state",
            "description",
            "required_skills",
        ]


class JobsActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activities
        exclude = [
            "hired",
            "proposals",
            "invitations",
        ]


class JobsDetailSerializer(serializers.ModelSerializer):
    client = ClientDetailSerializer()
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
            "active_state",
            "description",
            "required_skills",
        ]

    # Check if the user has proposed to the job
    def get_has_proposed(self, instance: Job):
        request = self.context.get("request")
        user: User | None = request.user if request else None

        # Check if the request user is authenticated
        if user and user.is_authenticated:

            # Retrieve the user profile information
            [freelancer, profile_name] = user.profile

            # Check if the user is a freelancer
            if profile_name.lower() == "freelancer":

                # Check if the user has proposed to the job
                has_proposed = (
                    Proposal.objects.select_related()
                    .filter(job=instance, freelancer=freelancer)
                    .exists()
                )

                # return a boolean value
                return has_proposed

        return False

    # Update the category and required-skills data to a list of strings
    def update_categories_and_skills(self, data):
        try:
            data.update(
                {
                    "category": data.get("category", "").split(","),
                    "required_skills": data.get("required_skills", "").split(","),
                }
            )
            return data
        except KeyError:
            pass
        return data

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        data = self.update_categories_and_skills(representation)

        return data
