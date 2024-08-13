import random
from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from jobs.models.job import JobStatusChoices
from users.models.user import User
from notifications.models import Notification
from contracts.models import Contract
from proposals.models import Proposal, ProposalStatusChoices
from contracts.serializers import (
    ContractCreateSerializer,
    ContractRetrieveSerializer,
)
from utilities.generator import get_serializer_error_message


class ContractCreateAPIView(GenericAPIView):

    def get(self, request, *args, **kwargs):
        user: User = request.user

        if not user.is_client:
            return Response(
                {"message": "Forbidden! Only clients are allowed"}, status=403
            )

        profile, profile_name = user.profile
        proposal_id = request.query_params.get("pid")

        try:
            with transaction.atomic():
                # get proposal meant for this client
                proposal = Proposal.objects.get(
                    id=proposal_id, job__client=profile, status="PENDING"
                )
                if proposal.contract.exists():  # type: ignore
                    return Response({"message": "Contract already exists"}, status=400)

                serializer = ContractRetrieveSerializer(instance=proposal)
                return Response(serializer.data, status=200)

        except Proposal.DoesNotExist:
            return Response({"message": "Bad request attempted"}, status=400)

        except Exception as e:
            return Response({"message": str(e)}, status=400)

    def post(self, request, *args, **kwargs):
        user: User = request.user

        if not user.is_client:
            return Response(
                {"message": "Forbidden! Only clients are allowed"}, status=403
            )

        profile, profile_name = user.profile

        proposal_id = request.data.get("pid")
        duration = request.data.get("duration")
        start_date = request.data.get("start_date")
        payment_method = request.data.get("payment_method")
        additional_terms = request.data.get("additional_terms")

        try:
            # get proposal meant for this client
            with transaction.atomic():
                proposal = Proposal.objects.select_for_update().get(
                    id=proposal_id,
                    job__client=profile,
                    status=ProposalStatusChoices.PENDING,
                )
                if proposal.contract.exists():  # type: ignore
                    return Response(
                        {"message": "A contract for this proposal already exists"},
                        status=400,
                    )

                serializer = ContractCreateSerializer(
                    data={
                        "proposal": proposal.pk,
                        "job": proposal.job.pk,
                        "client": profile.pk,
                        "freelancer": proposal.freelancer.pk,
                        "duration": proposal.duration,
                        "start_date": start_date,
                        "additional_terms": additional_terms,
                    }
                )
                if serializer.is_valid():
                    contract: Contract = serializer.save()  # type: ignore

                    notifications = []

                    freelancer_notification = Notification()
                    notifications.append(freelancer_notification)
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
                        "You've received a contract for <strong>%s</strong> project, from freelancer <strong>%s</strong>. Please check it out."
                        % (proposal.job.title, proposal.job.client.user.name)
                    )
                    freelancer_notification.object_api_link = (
                        "/contracts/view/%s" % contract.pk
                    )
                    # ----------------------------------------------------------------------------

                    client_notification = Notification()
                    notifications.append(client_notification)

                    client_notification.recipient = proposal.job.client.user
                    client_messages = [
                        "New Contract",
                        "You've got a new contract.",
                        "A new contract has been created for you.",
                        "You have a new contract for your project",
                    ]
                    client_notification.hint_text = random.choice(client_messages)
                    client_notification.content_text = (
                        "You've created a contract for <strong>%s</strong> project, with <strong>%s</strong>. Please check it out."
                        % (proposal.job.title, proposal.freelancer.user.name)
                    )
                    client_notification.object_api_link = (
                        "/contracts/view/%s" % contract.pk
                    )
                    # --------------------------------------------------------------------

                    # update the main proposal status
                    proposal.status = ProposalStatusChoices.ACCEPTED
                    proposal.save()

                    # inactive other proposals
                    Proposal.objects.filter(job=proposal.job).exclude(
                        id=proposal.pk,
                    ).update(status=ProposalStatusChoices.DECLINED)

                    # update job status
                    proposal.job.published = False
                    proposal.job.status = JobStatusChoices.CLOSED
                    proposal.job.save()

                    # update job activities
                    job_activity = proposal.job.activities
                    job_activity.hired.add(proposal.freelancer)

                    # Save notifications
                    Notification.objects.bulk_create(notifications)
                    # TODO: Notify 7 through email

                    return Response(
                        {
                            "contract_id": contract.pk,
                            "message": "Contract created successfully",
                        },
                        status=200,
                    )
                error_message = get_serializer_error_message(serializer.errors)
                return Response({"message": error_message}, status=400)
        except Proposal.DoesNotExist:
            return Response({"message": "Proposal does not exist"}, status=400)
        except Exception as e:
            return Response({"message": str(e)}, status=400)
