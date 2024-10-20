from rest_framework import serializers
from contracts.models import Contract


class ContractCreateSerializer(serializers.ModelSerializer):
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
