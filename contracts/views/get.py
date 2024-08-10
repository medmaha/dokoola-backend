from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from contracts.models import Contract
from contracts.serializers import (
    ContractListSerializer,
)


class ContractListAPIView(ListAPIView):
    serializer_class = ContractListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Contract.objects.filter(
            Q(freelancer__user=user) | Q(client__user=user)
        ).order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class ContractRetrieveAPIView(RetrieveAPIView):
    serializer_class = ContractListSerializer

    def get_queryset(self, contract_id):
        user = self.request.user
        try:
            queryset = Contract.objects.get(
                Q(freelancer__user=user) | Q(client__user=user), id=contract_id
            )
            return queryset
        except:
            return None

    def retrieve(self, request, contract_id, *args, **kwargs):
        queryset = self.get_queryset(contract_id)
        if not queryset:
            return Response({"message": "Resource not found"}, status=404)

        serializer = self.get_serializer(
            instance=queryset, context={"request": request}
        )

        return Response(serializer.data, status=200)
