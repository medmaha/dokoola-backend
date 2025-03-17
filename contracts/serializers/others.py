from rest_framework import serializers

from proposals.models import Proposal


class ContractRelatedDataSerializer(serializers.Serializer):

    class Meta:
        model = Proposal
        fields = []

    def to_representation(self, instance: Proposal):
        return get_related_fields(instance)


def get_related_fields(instance: Proposal):
    data = {}
    data["job"] = {
        "public_id": instance.job.public_id,
        "title": instance.job.title,
        "description": instance.job.description[:400],
        "location": instance.job.address,
        "budget": instance.budget,
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
        "public_id": instance.talent.public_id,
        "avatar": instance.talent.user.avatar,
        "rating": instance.talent.average_rating(),
    }

    data["client"] = {
        "id": instance.job.client.pk,
        "name": instance.job.client.user.get_full_name(),
        "public_id": instance.job.client.public_id,
        "avatar": instance.job.client.user.avatar,
        "rating": instance.job.client.average_rating(),
    }

    return data
