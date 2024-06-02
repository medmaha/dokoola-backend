import random
from django.db import transaction
from django.db.models import Q
from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from notifications.models import Notification
from contracts.models import Contract
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

    def perform_update(self, contract_id: str):
        with transaction.atomic():
            user = self.request.user
            _, profile_name = user.profile  # type: ignore
            try:
                contract = Contract.objects.get(
                    Q(freelancer__user=user) | Q(client__user=user), id=contract_id
                )
                if profile_name.lower() == "client":
                    if contract.client_acknowledgement != "PENDING":
                        return None
                    contract.client_acknowledgement = "ACCEPTED"
                    contract.status = contract.freelancer_acknowledgement
                    contract.save()

                    Notification.objects.create(
                        hint_text="Project Acknowledged",
                        content_text=f"You've acknowledged a contract with <strong>{contract.freelancer.user.name}</strong>",
                        recipient=contract.freelancer.user,
                        object_api_link=f"/contracts/view/{contract.pk}",
                    )
                    # TODO: Notify 1 through email

                if profile_name.lower() == "freelancer":
                    if contract.freelancer_acknowledgement != "PENDING":
                        return None
                    contract.freelancer_acknowledgement = "ACCEPTED"
                    contract.status = contract.client_acknowledgement
                    contract.save()

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
                    # TODO: Notify 3 through email

                if contract.status == "ACCEPTED":
                    contract.progress = "ACTIVE"

                    Notification.objects.create(
                        hint_text="Project Started",
                        content_text=f"Your contract <strong>{contract.job.title}</strong> from <strong>{contract.client.user.name}</strong> is due an active",
                        recipient=contract.freelancer.user,
                        object_api_link=f"/contracts/view/{contract.pk}",
                    )
                    # TODO: Notify 5 through email

                    Notification.objects.create(
                        hint_text="Project Started",
                        content_text=f"Your contract <strong>{contract.job.title}</strong> with <strong>{contract.freelancer.user.name}</strong> has commenced",
                        recipient=contract.client.user,
                        object_api_link=f"/contracts/view/{contract.pk}",
                    )
                    # TODO: Notify 6 through email

                    contract.job.status = "IN_PROGRESS"
                    contract.job.save()
                contract.save()
                return contract
            except:
                return None

    def update(self, request, contract_id, *args, **kwargs):
        updated_contract = self.perform_update(contract_id)
        if not updated_contract:
            return Response({"message": "Resource not found"}, status=404)
        serializer = self.get_serializer(
            instance=updated_contract, context={"request": request}
        )
        return Response(serializer.data, status=200)


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
                        % proposal.job.title
                        % proposal.freelancer.user.name
                    )
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
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=400)
