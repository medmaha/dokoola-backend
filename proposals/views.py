import re
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    GenericAPIView,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from freelancers.models import Freelancer
from jobs.models import Job
from .models import Proposal, Attachment

from .serializers import (
    ProposalCreateSerializer,
    ProposalListSerializer,
    ProposalEditSerializer,
    ProposalUpdateSerializer,
)

from users.models import User
from utilities.text import get_url_search_params


class ProposalListApiView(ListAPIView):
    serializer_class = ProposalListSerializer

    def get_queryset(self):
        queryset = None
        username = get_url_search_params(self.request.get_full_path()).get("u")
        if username:
            user = User.objects.filter(username=username).first()
            if user:
                [profile, profile_name] = user.profile

                # Check if the user is a client or a freelancer
                if profile_name.lower() == "client":
                    # Gets all proposals for jobs that the client has posted
                    queryset = Proposal.objects.filter(job__client=profile).order_by(
                        "-updated_at", "is_accepted"
                    )
                # Gets all proposals for jobs that the freelancer has applied to
                elif profile_name.lower() == "freelancer":
                    queryset = Proposal.objects.filter(freelancer=profile).order_by(
                        "-updated_at", "is_accepted"
                    )
                else:
                    queryset = []
        return queryset

    def list(self, request, *args, **kwargs):
        print("hits")
        queryset = self.get_queryset()
        if queryset:
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        return Response({"message": "Request is forbidden"}, status=403)


class ProposalUpdateAPIView(GenericAPIView):
    serializer_class = ProposalUpdateSerializer

    def get(self, request, *args, **kwargs):
        url = request.get_full_path()
        proposal_id = get_url_search_params(url).get("slug")

        if proposal_id:
            proposal = Proposal.objects.filter(id=proposal_id).first()
            if proposal:
                [profile, _] = request.user.profile
                if proposal.freelancer.pk == profile.pk:
                    serializer = self.get_serializer(
                        proposal, context={"request": request}
                    )
                    return Response(serializer.data, status=200)
            return Response({"message": "Request is forbidden"}, status=400)

        return Response({"message": "Invalid proposal"}, status=400)

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
                instance=proposal, data=request.data, context={"request": request}
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)

                # return Response({'message':'Request is forbidden'}, status=400)
            return Response({"message": "Request is forbidden"}, status=400)
        return Response({"message": "Invalid proposal"}, status=400)


class ProposalCreateAPIView(CreateAPIView):
    """An API View for handling the creation of proposals"""

    serializer_class = ProposalCreateSerializer

    # Fires when a POST request is made
    def create(self, request: Request, *args, **kwargs):
        user: User = request.user
        freelancer, profile_type = user.profile

        # Make sure the user is a freelancer
        if profile_type.lower() != "freelancer":
            return Response(
                {"message": "Forbidden! Only freelancers can apply for jobs"},
                status=403,
            )

        # Copy the request data to avoid mutating the original request
        data: dict = request.data.copy()  # type: ignore

        try:
            # Check if the job exists
            job = Job.objects.select_related().get(slug=data.get("job", ""))

            # Check if the user has already applied for this job
            existing_proposal = Proposal.objects.filter(
                job=job, freelancer=freelancer, is_accepted=False
            ).exists()

            # If the user has already applied for this job, return an error
            if existing_proposal:
                return Response({"message": "Already applied for this job"}, status=400)

        # If the job doesn't exist, return an error
        except Job.DoesNotExist:
            return Response({"message": "Bad request attempted"}, status=400)

        except Exception as e:
            # If an unexpected error occurs, return an error
            return Response({"message": "An unexpected error occurred"}, status=400)

        # Get the attachment data of the request
        attachment_data = data.get("attachments")  # TODO: Handle attachments

        # Remove the attachment data from the request data
        data.pop("attachments", None)

        serializer = self.get_serializer(data=data, context={"request": request})

        if serializer.is_valid():
            proposal: Proposal = serializer.save(job=job, freelancer=freelancer)
            job.activities.proposals.add(proposal)
            job.activities.save()
            freelancer.bits = freelancer.bits - proposal.bits_amount
            freelancer.save()
            return Response(serializer.data, status=201)

        return Response({"message": "Bad request"}, status=400)

    def get_serializer(self, *args, **kwargs) -> ProposalCreateSerializer:
        return super().get_serializer(*args, **kwargs)


class ProposalCheckAPIView(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        freelancer = Freelancer.objects.filter(user=user).first()

        if not freelancer:
            return Response(
                {"message": "You don't have permission for this request"}, status=403
            )

        slug = self.kwargs.get("slug")
        job = Job.objects.filter(slug=slug).first()

        if not job:
            return Response({"message": "Request rejected"}, status=400)

        proposal = Proposal.objects.filter(job=job, freelancer=freelancer).exists()

        return Response({"proposed": proposal}, status=200)
