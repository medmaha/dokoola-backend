import json

from rest_framework import serializers

from jobs.models import Job
from users.serializer import UserSerializer

from .models import Client, Company, Review


class UpdateSerializer(serializers.ModelSerializer):

    @classmethod
    def merge_serialize(cls, instance, validated_data):
        data = dict()

        _meta = cls.Meta  # type: ignore

        for field in _meta.fields:
            if field in validated_data:
                data[field] = validated_data[field]
            else:
                data[field] = getattr(instance, field)

        return cls(instance=instance, data=data)


# -------------------------- Company ------------------------------ #


class CompanyCreateSerializer(serializers.ModelSerializer):
    """
    A serializer for the company list api view
    Use to get the list of companies without much extra information
    """

    class Meta:
        model = Company
        fields = [
            "name",
            "website",
            "logo_url",
            "industry",
            "description",
            "date_established",
        ]


class CompanyUpdateSerializer(UpdateSerializer, serializers.ModelSerializer):
    """
    A serializer for the company update view
    Expose the company's updatable fields
    """

    class Meta:
        model = Company
        fields = [
            "name",
            "website",
            "logo_url",
            "industry",
            "description",
            "date_established",
        ]


# -------------------------- Client ------------------------------ #


class ClientMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "country",
            "public_id",
        ]

    def to_representation(self, instance: Client):
        data = super().to_representation(instance)

        data["full_name"] = instance.name
        data["avatar"] = instance.user.avatar

        data["company"] = None
        if instance.company:
            data["company"] = {
                "slug": instance.company.slug,
                "name": instance.company.name,
            }
        return data


class ClientCreateSerializer(serializers.ModelSerializer):
    """
    A serializer for the client list api view
    Use to get the list of clients without much extra information
    """

    class Meta:
        model = Client
        fields = ["address", "country", "about"]


class ClientListSerializer(serializers.ModelSerializer):
    """
    A serializer for the client list api view
    Use to get the list of clients without much extra information
    """

    class Meta:
        model = Client
        fields = [
            "id",
            "country",
            "address",
            "public_id",
        ]

    def to_representation(self, instance: Client):
        data = super().to_representation(instance)

        data["full_name"] = instance.name

        data["company"] = None
        if instance.company:
            data["company"] = {
                "slug": instance.company.slug,
                "name": instance.company.name,
            }

        data["avatar"] = instance.user.avatar
        data["avg_rating"] = instance.average_rating()

        return data


class ClientUpdateSerializer(UpdateSerializer, serializers.ModelSerializer):
    """
    This serializer is used for the client update view
    Expose the client's updatable fields
    """

    class Meta:
        model = Client
        fields = [
            "country",
            "address",
            "about",
        ]

    def validate_country(self, value):
        if value is None:
            return {}
        try:
            if isinstance(value, dict):
                return value
            return json.loads(value)

        except Exception as e:
            raise serializers.ValidationError("Country: {}".format(e))


class ClientRetrieveSerializer(serializers.ModelSerializer):
    """
    A serializer for the client detail api view \n
    Securely serialize all the necessary information of this client
    * The return data will vary depending on the requesting user
    """

    class Meta:
        model = Client
        fields = [
            "id",
            "public_id",
            "country",
            "address",
            "about",
        ]

    def to_representation(self, instance: Client):
        data = super().to_representation(instance)

        data["full_name"] = instance.name

        data["company"] = None
        if instance.company:
            data["company"] = {
                "id": instance.company.pk,
                "slug": instance.company.slug,
                "name": instance.company.name,
                "website": instance.company.website,
                "logo_url": instance.company.logo_url,
                "industry": instance.company.industry,
                "description": instance.company.description,
                "date_established": instance.company.date_established,
            }

        data["email"] = instance.user.email
        data["avatar"] = instance.user.avatar
        data["username"] = instance.user.username
        data["first_name"] = instance.user.first_name
        data["last_name"] = instance.user.last_name
        data["last_name"] = instance.user.last_name
        data["phone"] = instance.user.phone
        data["gender"] = instance.user.gender
        data["avg_rating"] = instance.average_rating()
        data["profile_type"] = "Client"

        return data


class ClientUpdateDataSerializer(serializers.ModelSerializer):
    """
    A readonly serializer for retrieving the updatable data of a client

    """

    class Meta:
        model = Client
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

    def to_representation(self, instance: Review):
        data = super().to_representation(instance)
        data["author"] = (
            {
                "public_id": instance.author.public_id,
                "avatar": instance.author.avatar,
                "name": instance.author.name,
            }
            if instance.author
            else None
        )


class ClientJobDetailSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the job detail view
    * The return data will vary depending on the requesting user
    """

    class Meta:
        model = Client
        # TODO: fix me the exposed fields
        fields = "__all__"


class ClientJobPostingSerializer(serializers.ModelSerializer):
    """
    This serializer is used for the job detail view
    * The return data will vary depending on the requesting user
    """

    client = ClientMiniSerializer()

    class Meta:
        model = Job
        fields = "__all__"
