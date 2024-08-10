import random
from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from notifications.models import Notification
from contracts.models import Contract
from proposals.models import Proposal
from contracts.serializers import (
    ContractCreateSerializer,
    ContractRetrieveSerializer,
)


class ContractCreateAPIView(GenericAPIView):

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

            serializer = ContractRetrieveSerializer(instance=proposal)
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
                        % (proposal.job.title, proposal.freelancer.user.name)
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
        # except Exception as e:
        #
        #     return Response({"message": str(e)}, status=400)
