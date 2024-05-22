from django.db.models import Q
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from .search import FreelancersSearchAPIView

from .serializers import (
    FreelancerDetailSerializer,
    FreelancerSerializer,
    FreelancerMiniInfoSerializer,
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
