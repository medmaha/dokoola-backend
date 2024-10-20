from rest_framework import serializers
from contracts.models import Contract
from proposals.models import Proposal


class ContractUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            "start_date",
            "end_date",
            "duration",
            "additional_terms",
        ]

    def to_representation(self, instance: Contract):
        data = super().to_representation(instance)
        return {**data, **get_related_fields(instance.proposal)}


def get_related_fields(instance: Proposal):
    data = {}
    data["job"] = {
        "slug": instance.job.slug,
        "title": instance.job.title,
        "description": instance.job.description[:400],
        "location": instance.job.location,
        "budget": instance.job.budget,
        "payment_type": instance.job.payment_type,
        "duration": instance.duration,
    }
    data["proposal"] = {
        "id": instance.pk,
        "cover_letter": instance.cover_letter,
        "budget": instance.budget,
        "status": instance.status,
        "duration": instance.duration,
    }
    data["talent"] = {
        "id": instance.talent.pk,
        "name": instance.talent.user.get_full_name(),
        "username": instance.talent.user.username,
        "avatar": instance.talent.user.avatar,
        "rating": instance.talent.user.calculate_rating(),
    }

    data["client"] = {
        "id": instance.job.client.pk,
        "name": instance.job.client.user.get_full_name(),
        "username": instance.job.client.user.username,
        "avatar": instance.job.client.user.avatar,
        "rating": instance.job.client.average_rating(),
    }

    return data
