import datetime
from django.db import transaction
from django.db.models import Q
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.request import Request
from rest_framework.response import Response

from core.constants import DokoolaConstants
from core.services.after.main import AfterResponseService
from jobs.models import Job
from jobs.models.activities import Activities
from jobs.models.job import JobStatusChoices
from src.settings.logger import DokoolaLogger
from talents.models import Talent  # Updated import
from users.models import User
from utilities.generator import get_serializer_error_message

from .models import Attachment, Proposal, ProposalStatusChoices
from .serializers import (
    ProposalCreateSerializer,
    ProposalDetailSerializer,
    ProposalEditSerializer,
    ProposalListSerializer,
    ProposalPendingListSerializer,
    ProposalUpdateSerializer,
)


class ProposalListApiView(ListAPIView):
    serializer_class = ProposalListSerializer

    def get_queryset(self):
        username = self.request.query_params.get("u")  # type: ignore
        if username:
            user = User.objects.filter(username=username).first()
            if user:
                [profile, profile_name] = user.profile

                # Check if the user is a client or a talent
                if profile_name.lower() == "client":
                    # Gets all proposals for jobs that the client has posted
                    queryset = Proposal.objects.filter(job__client=profile).order_by(
                        "-updated_at"
                    )
                # Gets all proposals for jobs that the talent has applied to
                elif profile_name.lower() == "talent":
                    queryset = Proposal.objects.filter(talent=profile).order_by(
                        "-updated_at"
                    )
                else:
                    queryset = []
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class ProposalRetrieveApiView(RetrieveAPIView):
    serializer_class = ProposalDetailSerializer

    def get_queryset(self, publid_id: str):
        if not self.request.user.is_authenticated:
            return "Unauthorized! Please log in"

        user = self.request.user

        try:
            # Only retrieve proposals for the current user
            # and if the proposal is for the current user
            # or from the current user
            proposal = Proposal.objects.get(
                Q(job__client__user=user) | Q(talent__user=user),
                public_id=publid_id,
            )
        except Proposal.DoesNotExist:
            return "Proposal not found"
        except:
            return "Error! failed to get proposal"

        return proposal

    def retrieve(self, request, publid_id, *args, **kwargs):

        queryset = self.get_queryset(publid_id)

        if isinstance(queryset, str):
            return Response({"message": queryset}, status=400)
        serializer = self.get_serializer(queryset, context={"request": request})
        return Response(serializer.data, status=200)


class ProposalUpdateAPIView(GenericAPIView):
    serializer_class = ProposalUpdateSerializer

    def get(self, request, publid_id, *args, **kwargs):

        # Get the user and the profile
        user = request.user
        profile, profile_name = user.profile

        # Check if the user is a talent
        if profile_name.lower() != "talent":
            return Response({"message": "Bad request attempted"}, status=400)

        try:
            proposal = Proposal.objects.get(
                talent__id=profile.id,
                public_id=publid_id,
                status=ProposalStatusChoices.PENDING,
            )  # Get the proposal

            # Check if user is the owner of the proposal
            if proposal.talent != profile:
                return Response(
                    {
                        "message": "Forbidden! You are not allowed to perform this action"
                    },
                    status=403,
                )

            # Check if the proposal is pending
            if proposal.status != ProposalStatusChoices.PENDING:
                return Response({"message": "Bad request attempted"}, status=400)

            # Serialize the proposal
            serializer = self.get_serializer(proposal, context={"request": request})
            return Response(serializer.data, status=200)

        except Proposal.DoesNotExist:
            return Response({"message": "Bad request attempted"}, status=400)

        except Exception as e:
            return Response({"message": "An unexpected error occurred"}, status=400)

    def put(self, request, publid_id, *args, **kwargs):
        # Get the user and the profile
        user = request.user
        profile, profile_name = user.profile

        try:
            with transaction.atomic():
                self.serializer_class = ProposalEditSerializer

                proposal = Proposal.objects.get(public_id=publid_id)

                # Proposal review update
                # Check if the review query parameter is present
                if "review" in request.query_params:
                    if proposal.status == ProposalStatusChoices.REVIEW:
                        return Response(status=204)
                    proposal.status = ProposalStatusChoices.REVIEW
                    proposal.save()
                    return Response(status=204)

                # Proposal status update
                if "status" in request.query_params:

                    # Check if to see if this proposal can be updated
                    if proposal.status == ProposalStatusChoices.ACCEPTED:
                        return Response(
                            {"message": "Proposal already accepted"}, status=400
                        )
                    if proposal.status == ProposalStatusChoices.TERMINATED:
                        return Response(
                            {"message": "Proposal already terminated"}, status=400
                        )
                    if proposal.status == ProposalStatusChoices.WITHDRAWN:
                        return Response(
                            {"message": "Proposal already withdrawn"}, status=400
                        )

                    _comment = request.data.get("comment", "")
                    _status = request.query_params.get("status", "").upper()

                    proposal.client_comment = _comment

                    if _status == ProposalStatusChoices.ACCEPTED:

                        if proposal.job.client != profile:
                            return Response(
                                {
                                    "message": "Forbidden! You are not allowed to perform this action"
                                },
                                status=403,
                            )

                        proposal.status = ProposalStatusChoices.ACCEPTED
                        proposal.save()

                        AfterResponseService.register(
                            proposal.notify_talent, ProposalStatusChoices.ACCEPTED
                        )
                        AfterResponseService.register(
                            proposal.job.notify_client,
                            JobStatusChoices.IN_PROGRESS,
                            proposal,
                        )
                        AfterResponseService.register(
                            proposal.job.update_status_and_withdraw_proposals,
                            job_status=JobStatusChoices.IN_PROGRESS,
                        )

                    elif _status == ProposalStatusChoices.DECLINED:

                        if proposal.job.client != profile:
                            return Response(
                                {
                                    "message": "Forbidden! You are not allowed to perform this action"
                                },
                                status=403,
                            )

                        proposal.status = ProposalStatusChoices.DECLINED
                        proposal.save()
                        AfterResponseService.register(
                            proposal.notify_talent, ProposalStatusChoices.DECLINED
                        )

                    elif _status == ProposalStatusChoices.TERMINATED:

                        if proposal.talent != profile:
                            return Response(
                                {
                                    "message": "Forbidden! You are not allowed to perform this action"
                                },
                                status=403,
                            )

                        proposal.status = ProposalStatusChoices.TERMINATED
                        proposal.save()
                        AfterResponseService.register(
                            proposal.notify_talent, ProposalStatusChoices.TERMINATED
                        )

                    else:
                        return Response({"message": "Invalid status"}, status=400)

                    return Response(status=204)

                # Check if user is the owner of the proposal
                if proposal.talent != profile:
                    return Response(
                        {
                            "message": "Forbidden! You are not allowed to perform this action"
                        },
                        status=403,
                    )

                # Check if the proposal is pending
                if proposal.status != ProposalStatusChoices.PENDING:
                    return Response({"message": "Bad request attempted"}, status=400)

                # Serialize the proposal
                serializer = self.get_serializer(
                    proposal, data=request.data, context={"request": request}
                )

                # Get the attachment data of the request
                attachment_data = request.data.get(
                    "attachments"
                )  # TODO: Handle attachments

                # If the serializer is valid, save the proposal
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "public_id": publid_id,
                            "message": "Proposal updated successfully",
                        },
                        status=200,
                    )

                error_message = get_serializer_error_message(serializer.errors)
                return Response({"message": error_message}, status=400)
        except Proposal.DoesNotExist:
            return Response({"message": "Bad request attempted"}, status=400)
        except Exception as e:
            print("error", e)
            return Response({"message": "An unexpected error occurred"}, status=400)


class ProposalCreateAPIView(CreateAPIView):
    """An API View for handling the creation of proposals"""

    serializer_class = ProposalCreateSerializer

    # Fires when a POST request is made
    def create(self, request: Request, *args, **kwargs):
        user: User = request.user
        talent, profile_type = user.profile

        # Make sure the user is a talent
        if profile_type.lower() != "talent":
            return Response(
                {"message": "Forbidden! Only talents can apply for jobs"},
                status=403,
            )

        # Copy the request data to avoid mutating the original request
        data: dict = request.data.copy()  # type: ignore

        # Execute this process in a db-transaction mode
        with transaction.atomic():
            try:
                # Check if the job exists
                job_public_id = data.get("job", "")
                job = Job.objects.select_related().get(public_id=job_public_id)

                # Check if the job is in published state
                if job.status != JobStatusChoices.PUBLISHED:
                    return Response(
                        {"message": "This job is not published"},
                        status=403,
                    )

                # Check if the user has already applied for this job
                existing_proposal = Proposal.objects.filter(
                    job=job, talent=talent
                ).exists()

                # If the user has already applied for this job, return an error
                if existing_proposal:
                    return Response(
                        {"message": "Already applied for this job"},
                        status=400,
                    )

            # If the job doesn't exist, return an error
            except Job.DoesNotExist:
                return Response({"message": "Job doesn't exist"}, status=400)

            # If an unexpected error occurs, log the error and return an error
            except Exception as e:
                log_data = {
                    "event": "ProposalCreateAPIView",
                    "exception": str(e),
                    "user_id": user.public_id,
                    "request_path": request.path,
                    "request_method": request.method,
                    "timestamp": datetime.datetime.now().__str__(),
                    "job_public_id": job_public_id,
                    "talent_public_id": talent.public_id,
                }
                DokoolaLogger.critical(log_data, extra=log_data)
                return Response({"message": "An unexpected error occurred"}, status=400)

            # Get the attachment data of the request
            attachment_data = data.pop("attachments", [])  # TODO: Handle attachments

            def after_response(proposal: Proposal):
                # Update the job's activity
                activity, _ = Activities.objects.get_or_create(job=job)
                activity.proposal_count = activity.proposal_count + 1
                activity.save()

                # Update the job's proposal count
                job.proposal_count = activity.proposal_count
                job.save()

                # Update the talent's bits
                talent.bits = talent.bits - proposal.bits_amount
                talent.save()

                proposal.job.notify_client(
                    JobStatusChoices.PUBLISHED, new_proposal=proposal
                )

            serializer = self.get_serializer(data=data, context={"request": request})
            if serializer.is_valid():

                # Create the proposal
                proposal: Proposal = serializer.save(
                    job=job,
                    talent=talent,
                    service_fee=DokoolaConstants.get_service_fee(),
                )

                AfterResponseService.register(after_response, proposal)

                return Response(
                    {
                        "public_id": proposal.public_id,
                        "message": "Proposal created successfully",
                    },
                    status=201,
                )

            # Get the error message from the serializer
            error_message = get_serializer_error_message(serializer.errors)
            return Response({"message": error_message}, status=400)

    def get_serializer(self, *args, **kwargs) -> ProposalCreateSerializer:
        return super().get_serializer(*args, **kwargs)


class ProposalCheckAPIView(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        talent = Talent.objects.filter(user=user).first()

        if not talent:
            return Response(
                {"message": "You don't have permission for this request"},
                status=403,
            )

        slug = self.kwargs.get("slug")
        job = Job.objects.filter(slug=slug).first()

        if not job:
            return Response({"message": "Request rejected"}, status=400)

        proposal = Proposal.objects.filter(job=job, talent=talent).exists()

        return Response({"proposed": proposal}, status=200)


class ProposalPendingListView(ListAPIView):
    serializer_class = ProposalPendingListSerializer

    def get_queryset(self, username: str):
        try:
            user = User.objects.get(username=username)
            talent = Talent.objects.select_related().get(user_id=user.pk)
        except User.DoesNotExist:
            return None
        except Talent.DoesNotExist:
            return None
        except Exception:
            return None
        proposals = Proposal.objects.filter(
            job__is_valid=True,
            talent=talent,
            status=ProposalStatusChoices.PENDING,
        )
        return proposals

    def list(self, request, username, *args, **kwargs):
        queryset = self.get_queryset(username)

        if queryset is None:
            return Response({"message": "This request is prohibited"}, status=403)
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)
