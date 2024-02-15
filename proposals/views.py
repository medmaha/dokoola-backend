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
    ProposalEditViewSerializer,
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
                if profile_name.lower() == "client":
                    queryset = Proposal.objects.filter(job__client=profile).order_by(
                        "-updated_at", "is_accepted"
                    )
                elif profile_name.lower() == "freelancer":
                    queryset = Proposal.objects.filter(freelancer=profile).order_by(
                        "-updated_at", "is_accepted"
                    )
                else:
                    queryset = []

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        return Response({"message": "Request is forbidden"}, status=403)


class ProposalUpdateAPIView(GenericAPIView):
    serializer_class = ProposalEditViewSerializer

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
        proposal_id = request.data.get("slug")
        self.serializer_class = ProposalEditSerializer

        if proposal_id:
            proposal = Proposal.objects.filter(id=proposal_id).first()
            if proposal:
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
    serializer_class = ProposalCreateSerializer

    def create(self, request: Request, *args, **kwargs):
        user = request.user
        freelancer = Freelancer.objects.filter(user=user).first()

        if not freelancer:
            return Response({"message": "Client can't apply for jobs"}, status=401)

        data: dict = request.data.copy()  # type: ignore

        job = Job.objects.filter(slug=data.get("job")).first()

        if not job:
            return Response({"message": "Bad request attempted"}, status=400)

        data["job"]

        activities = job.activities

        _data = {}
        _data["job"] = job
        _data["freelancer"] = freelancer

        del data["attachments"]

        serializer = self.get_serializer(data=data, context={"request": request})

        if serializer.is_valid():
            proposal = Proposal.objects.create(**{**data, **_data})
            activities.proposals.add(proposal)
            activities.save()
            freelancer.bits -= int(data["bits_amount"])
            freelancer.save()

            return Response(serializer.data, status=201)

        print(serializer.errors)

        message = ""
        return Response({"message": message}, status=400)

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

        print(slug)

        if not job:
            return Response({"message": "Request rejected"}, status=400)

        proposal = Proposal.objects.filter(job=job, freelancer=freelancer).exists()

        return Response({"proposed": proposal}, status=200)
