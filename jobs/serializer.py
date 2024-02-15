from rest_framework import serializers

from users.serializer import User
from clients.serializer import (
    ClientSerializer,
    ClientDetailSerializer,
    ClientMiniSerializer,
)
from proposals.models import Proposal

from .models import Job, Pricing


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
    client = ClientMiniSerializer()
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
            "description",
            "created_at",
        ]


class JobsSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Job
        fields = [
            "slug",
            "title",
            "client",
            "budget",
            "category",
            "location",
            "created_at",
            "description",
            "payment_type",
        ]

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        data = abstract_data(representation, instance, self)
        description = representation.get("description", "")
        data.update({"description": description[:200]})
        return data


class JobsDetailSerializer(serializers.ModelSerializer):
    client = ClientDetailSerializer()
    pricing = PricingSerializer()

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
            "created_at",
            "activities",
            "description",
            "required_skills",
        ]

    def to_representation(self, instance: Job):
        representation = super().to_representation(instance)
        data = abstract_data(representation, instance, self)

        return data


def abstract_data(representation, instance, self):
    request = self.context.get("request")
    data = {}
    if request:
        user: User = request.user
        if user and user.is_authenticated:
            [freelancer, profile_name] = user.profile
            if profile_name.lower() == "freelancer":
                has_proposed = Proposal.objects.filter(
                    job=instance, freelancer=freelancer
                ).exists()
                data.update({"has_proposed": has_proposed})

    try:
        category = representation.pop("category")
        required_skills = representation.pop("required_skills")
        if category:
            category = category.split(",")
        if required_skills:
            required_skills = required_skills.split(",")
        data.update(
            {
                "category": category,
                "required_skills": required_skills,
            }
        )
    except KeyError:
        pass

    return {**representation, **data}
