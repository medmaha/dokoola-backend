from rest_framework import serializers

from contracts.models import Contract
from proposals.models import Job, Proposal
from proposals.serializers import ProposalListSerializer


class ContractProposalSerializer:
    class Meta:
        model = Proposal
        fields = [
            "public_id",
        ]


class ContractJobSerializer:
    class Meta:
        model = Job
        fields = [
            "title",
            "public_id",
        ]


class ContractCreateSerializer(serializers.ModelSerializer):

    job = ContractJobSerializer()
    proposal = ContractProposalSerializer()

    class Meta:
        model = Contract
        fields = [
            "proposal",
            "talent",
            "job",
            "client",
            "start_date",
            "end_date",
            "duration",
            "additional_terms",
        ]
