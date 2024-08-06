import random
from django.db import transaction
from django.db.models import Q
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from notifications.models import Notification
from contracts.models import Contract, ContractProgressChoices
from proposals.models import Proposal
from contracts.serializers import (
    ContractListSerializer,
    ContractCreateSerializer,
    ContractCreateDataSerializer,
)


class ContractListAPIView(GenericAPIView):
    serializer_class = ContractListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Contract.objects.filter(
            Q(freelancer__user=user) | Q(client__user=user)
        ).order_by("-created_at")
        return queryset

    def get(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class ContractAcceptAPIView(UpdateAPIView):
    serializer_class = ContractListSerializer

    def perform_update(self, contract_id: str, new_status:str) -> str | Contract:
        with transaction.atomic():
            user = self.request.user
            _, profile_name = user.profile  # type: ignore
            try:
                contract = Contract.objects.get(
                    Q(freelancer__user=user) | Q(client__user=user), id=contract_id
                )

                # Check if user is a Client
                if profile_name.lower() == "client":
                    if contract.client_acknowledgement != "PENDING":
                        # Return error of the client has already acknowledges or rejects the contract
                        return f"Contract already {contract.client_acknowledgement.lower()} stage"
                    
                    # Update the client acknowledgement of the contract
                    contract.client_acknowledgement = new_status
                    contract.status = contract.freelancer_acknowledgement # Accepted | Rejected | Pending
                    contract.save()


                    if new_status == "ACCEPTED":
                        # Create a notification for this action
                        Notification.objects.create(
                            hint_text="Project Acknowledged",
                            content_text=f"You've acknowledged a contract with <strong>{contract.freelancer.user.name}</strong>",
                            recipient=contract.client.user,
                            object_api_link=f"/contracts/view/{contract.pk}",
                        )
                    else:
                        Notification.objects.create(
                            hint_text="Project Rejected",
                            content_text=f"You've rejected a contract you created with <strong>{contract.freelancer.user.name}</strong>",
                            recipient=contract.client.user,
                            object_api_link=f"/contracts/view/{contract.pk}",
                        )

                        # TODO: Notify 1 through email

                 # Check if user is a freelancer

                # Check if user is a Freelancer
                if profile_name.lower() == "freelancer":
                    if contract.freelancer_acknowledgement != "PENDING":
                        # Return None of the freelancer has already acknowledges or rejects the contract
                        return f"Contract already {contract.client_acknowledgement.lower()} stage"
                    
                    # Update the freelancer acknowledgement of the contract
                    contract.freelancer_acknowledgement = new_status
                    contract.status = contract.client_acknowledgement # Accepted | Rejected | Pending
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

    def update(self, request, contract_id:str, *args, **kwargs):
        new_status:str = request.data.get("status")

        if not new_status:
            return Response({"message": "Request body missing a status value"}, status=400)
        
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


class ContractCreateView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        user = request.user
        profile, profile_name = user.profile

        if profile_name.lower() != "client":
            return Response({"message": "Bad request attempted"}, status=400)

        proposal_id = request.query_params.get("pid")

        try:
            # get proposal meant for this client
            proposal = Proposal.objects.get(
                id=proposal_id, job__client=profile, status="PENDING"
            )

            if proposal.contract.exists():  # type: ignore
                Proposal.objects.filter(id=proposal_id).update(
                    status="ACCEPTED", is_accepted=True, is_pending=False
                )
                return Response({"message": "Contract already exists"}, status=400)

            serializer = ContractCreateDataSerializer(instance=proposal)
            Proposal.objects.select_related().filter(id=proposal_id).update(
                is_reviewed=True
            )
            return Response(serializer.data, status=200)

        except Proposal.DoesNotExist:
            return Response({"message": "Bad request attempted"}, status=400)

        except Exception as e:
            return Response({"message": str(e)}, status=400)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile, profile_name = user.profile

        if profile_name.lower() != "client":
            return Response({"message": "Bad request attempted"}, status=400)

        proposal_id = request.data.get("pid")
        duration = request.data.get("duration")
        start_date = request.data.get("start_date")
        payment_method = request.data.get("payment_method")
        additional_terms = request.data.get("additional_terms")

        try:
            # get proposal meant for this client
            with transaction.atomic():
                proposal = Proposal.objects.select_for_update().get(
                    id=proposal_id, job__client=profile, status="PENDING"
                )
                if proposal.contract.exists():  # type: ignore
                    Proposal.objects.select_related().filter(id=proposal_id).update(
                        status="ACCEPTED", is_accepted=True, is_pending=False
                    )
                    return Response({"message": "Contract already exists"}, status=400)

                serializer = ContractCreateSerializer(
                    data={
                        "proposal": proposal.pk,
                        "job": proposal.job.pk,
                        "client": profile.pk,
                        "freelancer": proposal.freelancer.pk,
                        "duration": duration,
                        "start_date": start_date,
                        "payment_method": payment_method,
                        "additional_terms": additional_terms,
                    }
                )
                if serializer.is_valid():
                    contract: Contract = serializer.save()  # type: ignore

                    # update other proposal proposal status
                    Proposal.objects.filter(job=proposal.job).exclude(
                        id=proposal.pk,
                    ).update(is_decline=True, is_pending=False, status="DECLINED")

                    freelancer_notification = Notification()
                    freelancer_notification.recipient = proposal.freelancer.user
                    freelancer_messages = [
                        "New Contract",
                        "You've got a new contract.",
                        "A new contract has been created for you.",
                        "You have a new contract for a project you've proposed to",
                    ]
                    freelancer_notification.hint_text = random.choice(
                        freelancer_messages
                    )

                    
                    freelancer_notification.content_text = (
                        "You've received a contract for <strong>%s<strong/> project, from <strong>%s<strong/>. Please check it out."
                        % ( proposal.job.title, proposal.freelancer.user.name
                    ))
                    freelancer_notification.object_api_link = (
                        "/contracts/view/%s" % contract.pk
                    )

                    # TODO: Notify 7 through email
                    freelancer_notification.save()

                    client_notification = Notification()
                    client_notification.recipient = proposal.job.client.user
                    client_messages = [
                        "New Contract",
                        "You've got a new contract.",
                        "A new contract has been created for you.",
                        "You have a new contract for a project you're working on.",
                    ]
                    client_notification.hint_text = random.choice(client_messages)
                    client_notification.content_text = (
                        "You've created a contract for <strong>%s<strong/> project, with <strong>%s<strong/>. Please check it out."
                        % (proposal.job.title, proposal.freelancer.user.name)
                    )
                    client_notification.object_api_link = (
                        "/contracts/view/%s" % contract.pk
                    )
                    proposal.status = "ACCEPTED"
                    proposal.is_pending = False
                    proposal.is_accepted = True
                    proposal.is_reviewed = True
                    proposal.job.activities.hired.add(proposal.freelancer)
                    proposal.save()
                    proposal.job.save()

                    # TODO: Notify 8 through email
                    client_notification.save()
                    return Response(
                        {
                            "contract_id": contract.pk,
                            "message": "Contract created successfully",
                        },
                        status=200,
                    )
                return Response({"message": str(serializer.errors)}, status=400)
        except Proposal.DoesNotExist:
            return Response({"message": "Bad request attempted"}, status=400)
        # except Exception as e:
        #     
        #     return Response({"message": str(e)}, status=400)
