from django.db import transaction
from django.db.models import Q
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from notifications.models import Notification
from contracts.models import Contract, ContractProgressChoices
from contracts.serializers import (
    ContractListSerializer,
)


class ContractAcceptAPIView(UpdateAPIView):
    serializer_class = ContractListSerializer

    def perform_update(self, contract_id: str, new_status: str) -> str | Contract:
        with transaction.atomic():
            user = self.request.user
            _, profile_name = user.profile  # type: ignore
            try:
                contract = Contract.objects.get(
                    Q(freelancer__user=user) | Q(client__user=user), id=contract_id
                )

                # Check if user is a Client
                if profile_name.lower() == "client":
                    return f"Contract already acknowledged by you"

                # Check if user is a Freelancer
                if profile_name.lower() == "freelancer":
                    if contract.freelancer_acknowledgement != "PENDING":
                        # Return None of the freelancer has already acknowledges or rejects the contract
                        return f"Contract already {contract.freelancer_acknowledgement.lower()} stage"

                    # Update the freelancer acknowledgement of the contract
                    contract.freelancer_acknowledgement = new_status
                    contract.status = new_status  # Accepted | Rejected | Pending
                    contract.save()

                    if new_status == "ACCEPTED":
                        # Create a notification for this action
                        Notification.objects.create(
                            hint_text="Contract Accepted",
                            content_text=f"You've accepted a contract from <strong>{contract.client.user.name}</strong>",
                            recipient=contract.freelancer.user,
                            object_api_link=f"/contracts/view/{contract.pk}",
                        )
                        # TODO: Notify 2 through email

                        Notification.objects.create(
                            hint_text="Contract Accepted",
                            content_text=f"<strong>{contract.freelancer.user.name}</strong> has accepted your contract for project <strong>{contract.job.title}</strong>",
                            recipient=contract.client.user,
                            sender=contract.freelancer.user,
                            object_api_link=f"/contracts/view/{contract.pk}",
                        )
                    else:
                        # Create a notification for this action
                        Notification.objects.create(
                            hint_text="Contract Rejected",
                            content_text=f"You've rejected a contract from <strong>{contract.client.user.name}</strong>",
                            recipient=contract.freelancer.user,
                            object_api_link=f"/contracts/view/{contract.pk}",
                        )
                        # TODO: Notify 2 through email

                        Notification.objects.create(
                            hint_text="Contract Rejected",
                            content_text=f"<strong>{contract.freelancer.user.name}</strong> has rejected your contract for project <strong>{contract.job.title}</strong>",
                            recipient=contract.client.user,
                            sender=contract.freelancer.user,
                            object_api_link=f"/contracts/view/{contract.pk}",
                        )
                    # TODO: Notify 3 through email

                contract.save()
                return contract
            except Contract.DoesNotExist:
                return "Contact does not exist."

    def update(self, request, contract_id: str, *args, **kwargs):
        new_status: str = request.data.get("status")

        if not new_status:
            return Response(
                {"message": "Request body missing a status value"}, status=400
            )

        new_status = new_status.upper()

        if not new_status in ["ACCEPTED", "REJECTED"]:
            return Response({"message": "Invalid status value"}, status=400)

        updated_contract = self.perform_update(contract_id, new_status)
        if isinstance(updated_contract, str):
            return Response({"message": updated_contract}, status=4043)
        serializer = self.get_serializer(
            instance=updated_contract, context={"request": request}
        )
        return Response(serializer.data, status=200)


class ContractCompleteAPIView(UpdateAPIView):

    def update(self, request, contract_id, *args, **kwargs):
        if not contract_id:
            return Response({"message": "Bad request"}, status=400)

        user = self.request.user
        _, profile_name = user.profile  # type: ignore

        if profile_name.lower() == "client":
            return Response({"message": "Forbidden"}, status=403)

        if profile_name.lower() == "freelancer":
            try:
                contract = Contract.objects.get(id=contract_id, freelancer__user=user)
                contract.progress = ContractProgressChoices.COMPLETED
                contract.save()

                # TODO: Notify 4 through email and create a notification for both users
                return Response(
                    {"message": "Contract completed successfully"}, status=200
                )
            except Exception as e:

                return Response({"message": "Resource not found"}, status=404)

        return Response({"message": "Bad request"}, status=400)
