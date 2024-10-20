from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from contracts.models.contract import ContractStatusChoices
from contracts.serializers.update import ContractUpdateSerializer
from utilities.generator import get_serializer_error_message
from notifications.models import Notification
from contracts.models import Contract, ContractProgressChoices


class ContractUpdateAPIView(UpdateAPIView):
    serializer_class = ContractUpdateSerializer

    def update(self, request, contract_id: str, *args, **kwargs):

        try:
            contract = Contract.objects.get(
                id=contract_id, status=ContractStatusChoices.PENDING
            )
        except Contract.DoesNotExist:
            return Response({"message": "Contract does not exist"}, status=403)

        serializer = self.get_serializer(contract, data=request.data)

        if not serializer.is_valid():
            error_message = get_serializer_error_message(serializer.errors)
            return Response({"message": error_message}, status=400)

        serializer.save()
        return Response({"message": "Contract updated successfully"}, status=200)


class ContractAcceptAPIView(UpdateAPIView):

    def update(self, request, contract_id: str, *args, **kwargs):

        try:
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response({"message": "Contract does not exist"}, status=403)

        accepted = request.data.get("accept", None)

        (request.data)

        if accepted is None:
            return Response(
                {"message": 'Request body missing a "accept" value'}, status=400
            )

        if accepted in ["true", True]:
            new_status = ContractStatusChoices.ACCEPTED
        elif accepted in ["false", False]:
            new_status = ContractStatusChoices.REJECTED
        else:
            return Response({"message": "Invalid accept value"}, status=400)

        contract.status = new_status
        notifications = []

        if contract.status == ContractStatusChoices.ACCEPTED:
            notifications.append(
                # Notify the talent
                Notification(
                    hint_text="Contract Accepted",
                    content_text=f"You've accepted a contract from <strong>{contract.client.user.name}</strong>",
                    recipient=contract.talent.user,
                    object_api_link=f"/contracts/view/{contract.pk}",
                ),
            )
            notifications.append(
                # Notify the client
                Notification(
                    hint_text="Contract Accepted",
                    content_text=f"<strong>{contract.talent.user.name}</strong> has accepted your contract for project <strong>{contract.job.title}</strong>",
                    recipient=contract.client.user,
                    sender=contract.talent.user,
                    object_api_link=f"/contracts/view/{contract.pk}",
                )
            )
        else:
            notifications.append(
                # Notify the talent
                Notification(
                    hint_text="Contract Rejected",
                    content_text=f"You've rejected a contract from <strong>{contract.client.user.name}</strong>",
                    recipient=contract.talent.user,
                    object_api_link=f"/contracts/view/{contract.pk}",
                ),
            )
            notifications.append(
                # Notify the client
                Notification(
                    hint_text="Contract Rejected",
                    content_text=f"<strong>{contract.talent.user.name}</strong> has rejected your contract for project <strong>{contract.job.title}</strong>",
                    recipient=contract.client.user,
                    sender=contract.talent.user,
                    object_api_link=f"/contracts/view/{contract.pk}",
                )
            )
        contract.talent_acknowledgement = new_status
        contract.save()
        Notification.objects.bulk_create(notifications)
        return Response({"message": "Contract updated successfully"}, status=200)


class ContractCompleteAPIView(UpdateAPIView):

    def update(self, request, contract_id, *args, **kwargs):
        if not contract_id:
            return Response({"message": "Bad request"}, status=400)

        user = self.request.user
        _, profile_name = user.profile  # type: ignore

        if profile_name.lower() == "client":
            return Response({"message": "Forbidden"}, status=403)

        if profile_name.lower() == "talent":
            try:
                contract = Contract.objects.get(id=contract_id, talent__user=user)
                contract.progress = ContractProgressChoices.COMPLETED
                contract.save()

                # TODO: Notify 4 through email and create a notification for both users
                return Response(
                    {"message": "Contract completed successfully"}, status=200
                )
            except Exception as e:

                return Response({"message": "Resource not found"}, status=404)

        return Response({"message": "Bad request"}, status=400)
