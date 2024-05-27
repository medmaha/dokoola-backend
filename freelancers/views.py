from django.db.models import Q
from rest_framework.generics import RetrieveAPIView, ListAPIView, GenericAPIView
from rest_framework.response import Response

from proposals.serializers import ProposalPendingListSerializer
from jobs.models import Job
from proposals.models import Proposal

from .search import FreelancersSearchAPIView

from .serializers import (
    FreelancerDetailSerializer,
    FreelancerSerializer,
    FreelancerMiniInfoSerializer,
    FreelancerUpdateSerializer,
    FreelancerUpdateDataSerializer,
)

from .models import Freelancer

# Create your views here.


class FreelancerListAPIView(ListAPIView):
    permission_classes = []
    authentication_classes = []

    serializer_class = FreelancerSerializer

    def get_queryset(self):
        return FreelancersSearchAPIView.make_query(self.request.query_params)  # type: ignore

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)


class FreelancerUpdateAPIView(GenericAPIView):
    """
    This view is used for the client mini api view
    Retrieves clients updatable information
    """

    permission_classes = []

    def get(self, request, username, **kwargs):
        self.serializer_class = FreelancerUpdateDataSerializer
        try:
            freelancer = Freelancer.objects.get(user__username=username)
            freelancer_serializer: FreelancerUpdateDataSerializer = self.get_serializer(
                instance=freelancer, context={"request": request}
            )
            print(freelancer_serializer.data)
            return Response(freelancer_serializer.data, status=200)
        except Freelancer.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )

    def put(self, request, username, **kwargs):
        self.serializer_class = FreelancerUpdateSerializer
        try:
            client = Freelancer.objects.get(user__username=username)
            client_serializer: FreelancerUpdateSerializer = self.get_serializer(
                instance=client, data=request.data, context={"request": request}
            )

            if not client_serializer.is_valid():
                # raised the same error as the serializer
                return Response(str(client_serializer.errors), status=400)
            client_serializer.save()
            return Response(client_serializer.data, status=200)
        except Freelancer.DoesNotExist:
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )
        except Exception as e:
            print("Exception:", e)
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )


class FreelanceMiniInfoView(RetrieveAPIView):
    serializer_class = FreelancerMiniInfoSerializer

    def retrieve(self, request, username, **kwargs):
        freelancer = Freelancer.objects.filter(user__username=username).first()

        if not freelancer:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(freelancer)

        return Response(serializer.data, status=200)


class FreelanceRetrieveAPIView(RetrieveAPIView):
    serializer_class = FreelancerDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        username = self.kwargs.get("username")
        freelancer = Freelancer.objects.filter(user__username=username).first()

        if not freelancer:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(freelancer)

        return Response(serializer.data, status=200)


class FreelancerProjectsList(ListAPIView):
    serializer_class = ProposalPendingListSerializer

    def get_queryset(self, username: str):
        try:
            freelancer = Freelancer.objects.select_related().get(
                user__username=username
            )
        except Freelancer.DoesNotExist:
            return None
        proposals = Proposal.objects.filter(job__is_valid=True, freelancer=freelancer)
        return proposals

    def list(self, request, username, *args, **kwargs):
        queryset = self.get_queryset(username)
        if not queryset:
            return Response({"message": "This request is prohibited"}, status=403)
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
