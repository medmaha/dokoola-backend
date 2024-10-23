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

from jobs.models import Job
from jobs.models.activities import Activities
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


class ProposalDetailsApiView(RetrieveAPIView):
    serializer_class = ProposalDetailSerializer

    def get_queryset(self, proposal_id: str):
        if not self.request.user.is_authenticated:
            return "Unauthorized! Please log in"

        user = self.request.user

        try:
            # Only retrieve proposals for the current user
            # and if the proposal is for the current user
            # or from the current user
            proposal = Proposal.objects.get(
                Q(job__client__user=user) | Q(talent__user=user),
                pk=proposal_id,
            )
        except Proposal.DoesNotExist:
            return "Proposal not found"
        except:
            return "Error! failed to get proposal"

        return proposal

    def retrieve(self, request, pid, *args, **kwargs):
        queryset = self.get_queryset(pid)

        if isinstance(queryset, str):
            return Response({"message": queryset}, status=400)
        serializer = self.get_serializer(queryset, context={"request": request})
        return Response(serializer.data, status=200)


class ProposalUpdateAPIView(GenericAPIView):
    serializer_class = ProposalUpdateSerializer

    def get(self, request, *args, **kwargs):
        proposal_id = self.request.query_params.get("slug")  # type: ignore
        if not proposal_id:
            return Response({"message": "Invalid proposal"}, status=400)

        user = request.user

        [profile, profile_name] = user.profile

        if profile_name.lower() != "talent":
            return Response({"message": "Bad request attempted"}, status=400)

        try:
            proposal = Proposal.objects.get(
                talent=profile,
                id=proposal_id,
                status=ProposalStatusChoices.PENDING,
            )
            serializer = self.get_serializer(proposal, context={"request": request})
            return Response(serializer.data, status=200)
        except Proposal.DoesNotExist:
            return Response({"message": "Bad request attempted"}, status=400)

        except:
            return Response({"message": "An unexpected error occurred"}, status=400)

    def put(self, request, *args, **kwargs):
        proposal_id = request.data.get("proposal_id")
        self.serializer_class = ProposalEditSerializer

        if proposal_id:
            try:
                proposal = Proposal.objects.get(id=proposal_id)
            except Proposal.DoesNotExist:
                return Response({"message": "Bad request attempted"}, status=400)
            except:
                return Response({"message": "An unexpected error occurred"}, status=400)

            # Get the attachment data of the request
            attachment_data = request.data.get(
                "attachments"
            )  # TODO: Handle attachments

            serializer = self.get_serializer(
                instance=proposal,
                data=request.data,
                context={"request": request},
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

                # return Response({'message':'Request is forbidden'}, status=400)
            error_message = get_serializer_error_message(serializer.errors)
            return Response({"message": error_message}, status=400)
        return Response({"message": "Proposal does not exist"}, status=400)


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

        with transaction.atomic():
            try:
                # Check if the job exists
                job = Job.objects.select_related().get(slug=data.get("job", ""))

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

            except Exception as e:
                log_data = {
                    "event": "Exception in ProposalCreateAPIView",
                    "exception": str(e),
                    "user_id": user.pk,
                }
                DokoolaLogger.critical(log_data, extra=log_data)
                return Response({"message": "An unexpected error occurred"}, status=400)

            # Get the attachment data of the request
            attachment_data = data.pop("attachments", [])  # TODO: Handle attachments

            serializer = self.get_serializer(data=data, context={"request": request})

            if serializer.is_valid():
                proposal: Proposal = serializer.save(job=job, talent=talent)
                activity: Activities = job.activities
                activity.proposal_count = activity.proposal_count + 1
                activity.save()
                talent.bits = talent.bits - proposal.bits_amount
                talent.save()
                return Response(
                    {
                        "proposal_id": proposal.pk,
                        "message": "Proposal created successfully",
                    },
                    status=201,
                )

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
