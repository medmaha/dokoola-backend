from django.db import transaction
from django.db.models import Q
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.response import Response

from contracts.models import Contract, ContractProgressChoices
from contracts.models.contract import ContractStatusChoices
from contracts.serializers.retrieve import ContractListSerializer
from contracts.serializers.update import ContractUpdateSerializer
from notifications.models import Notification
from users.models.user import User


def generate_content_text(contract: Contract, accepted: bool = False):
    return ""


class ContractAPIView(GenericAPIView):

    def get_queryset(self, contract_id=None, query_params=None):
        try:
            user = self.request.user
            owner_identity = Q(talent__user=user) | Q(client__user=user)
            if contract_id:
                query_params = query_params or dict()
                is_proposal_id = query_params.get("pid", None)

                if is_proposal_id:
                    identity_query = Q(proposal__public_id=contract_id)
                else:
                    identity_query = Q(public_id=contract_id)

                identity_query = identity_query & owner_identity
                queryset = Contract.objects.get(identity_query)
            else:
                identity_query = owner_identity
                queryset = Contract.objects.filter(identity_query)
            return queryset
        except:
            return None

    def get(self, request, contract_id=None, *args, **kwargs):
        queryset = self.get_queryset(contract_id, request.query_params)
        if not queryset:
            return Response({"message": "Resource not found"}, status=404)

        get_list = contract_id is None

        # If no contract_id provided then we are dealing with a list of queryset
        if get_list:
            self.serializer_class = ContractListSerializer
            # Paginate the queryset list
            page = self.paginate_queryset(queryset)
            if page is not None:
                # use the paginated data as the queryset
                queryset = page
        else:
            self.serializer_class = ContractListSerializer

        serializer = self.get_serializer(instance=queryset, many=get_list, context={})

        if get_list:
            # let's return a paginator response
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data, status=200)

    def put(self, request, contract_id: str, *args, **kwargs):
        self.serializer_class = ContractUpdateSerializer

        try:
            user: User = request.user

            with transaction.atomic():

                contract = Contract.objects.get(public_id=contract_id)

                if "acknowledgement" in request.query_params:
                    assert (
                        contract.talent.public_id == user.public_id
                    ), "403: Forbidden request!"

                    accepted = request.data.get("accept", False)

                    err_status, err_msg = accept_or_reject_contract_for_talent(
                        contract, accepted
                    )
                    if err_status:
                        return Response({"message": err_msg}, status=err_status)

                    return Response(
                        {
                            "_id": contract.public_id,
                            "message": "Contract updated successfully",
                        },
                        status=200,
                    )

                assert (
                    contract.client.public_id == user.public_id
                ), "403: Forbidden request!"

                if contract.status != ContractStatusChoices.PENDING:
                    return Response(
                        {"message": "Contract cannot be edited"},
                        status=403,
                    )

                Contract.objects.select_for_update().filter(pk=contract.pk).update(
                    duration=request.data.get("duration", contract.duration),
                    end_date=request.data.get("end_date", contract.end_date),
                    start_date=request.data.get("start_date", contract.start_date),
                    additional_terms=request.data.get(
                        "additional_terms", contract.additional_terms
                    ),
                )
                return Response(
                    {
                        "_id": contract.public_id,
                        "message": "Contract updated successfully",
                    },
                    status=200,
                )

        except Contract.DoesNotExist:
            # TODO: log error
            return Response({"message": "Contract does not exist"}, status=404)

        except AssertionError as e:
            # TODO: log error
            return Response({"message": str(e)}, status=403)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Internal Server Error"}, status=500)


class ContractCompleteAPIView(UpdateAPIView):

    serializer_class = ContractUpdateSerializer

    def update(self, request, contract_id, *args, **kwargs):
        if not contract_id:
            return Response({"message": "Bad request"}, status=400)

        user = self.request.user
        _, profile_name = user.profile  # type: ignore

        if profile_name.lower() == "client":
            return Response({"message": "Forbidden"}, status=403)

        try:
            contract = Contract.objects.select_for_update().get(
                id=contract_id, talent__user=user
            )

            assert (
                contract.talent.public_id == request.user.public_id
            ), "403: Forbidden request"
            assert (
                contract.progress == ContractProgressChoices.ACTIVE
            ), "Contract cannot be completed"

            contract.progress = ContractProgressChoices.COMPLETED
            contract.save()

            return Response(
                {"message": "Contract completed successfully"},
                status=200,
            )
        except Contract.DoesNotExist:
            # TODO: log error
            return Response({"message": "Resource not found"}, status=404)

        except AssertionError as e:
            # TODO: log error
            error_message = str(e)
            return Response({"message": error_message}, status=403)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Internal Server Error"}, status=500)


def accept_or_reject_contract_for_talent(contract: Contract, accepted: bool):

    if accepted is None:
        return [400, 'Request body missing a "accept" value']

    if accepted in ["true", True]:
        new_status = ContractStatusChoices.ACCEPTED
    elif accepted in ["false", False]:
        new_status = ContractStatusChoices.REJECTED
    else:
        return [400, "Invalid accept value"]

    contract.status = new_status
    contract.talent_acknowledgement = new_status
    contract.save()

    notifications = []
    Notification.objects.bulk_create(
        [
            Notification(
                hint_text="Contract Accepted" if accepted else "Contract Rejected",
                content_text=generate_content_text(contract, accepted),
                recipient=recipient,
                sender=sender if not accepted else None,
                object_api_link=f"/contracts/{contract.pk}",
            )
            for recipient, sender in [
                (contract.talent.user, None),
                (contract.client.user, contract.talent.user),
            ]
        ]
    )

    Notification.objects.bulk_create(notifications)
    return [None, ""]
