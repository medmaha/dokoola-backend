from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from .serializers import FreelancerDetailSerializer, FreelancerSerializer

from .models import Freelancer

# Create your views here.


class FreelancerListAPIView(ListAPIView):
    permission_classes = []
    authentication_classes = []

    serializer_class = FreelancerSerializer

    def get_query_queryset(self):
        search_params = self.request.query_params # types:ignore

        category = search_params.get("category")
        location = search_params.get("location")
        badge = search_params.get("badge")
        rate = search_params.get("rate")

        _none = (not category) and (not location) and (not badge) and (not rate)

        print(_none)

        if _none:
            return Freelancer.objects.filter()

        queryset = Freelancer.objects.filter()

        matches = None

        if category:
            if category.lower() != "all":
                category = category.replace("%20", " ")
                queryset = Freelancer.objects.filter(
                    Q(skills__icontains=category)
                    | Q(title__icontains=category)
                    | Q(bio__icontains=category)
                    | Q(education__course__icontains=category)
                    | Q(education__description__icontains=category)
                )
            if not matches:
                matches = queryset

        if badge:
            if badge.lower() != "all":
                badge = badge.replace("%20", " ")
                queryset = Freelancer.objects.filter(Q(badge__icontains=badge))
            if matches:
                matches = matches | queryset
            else:
                matches = queryset

        if location:
            if location.lower() != "all":
                location = location.replace("%20", " ")
                queryset = Freelancer.objects.filter(
                    Q(country__icontains=location)
                    | Q(region__icontains=location)
                    | Q(city__icontains=location)
                    | Q(address__icontains=location)
                    | Q(zip_code__icontains=location)
                )
            if matches:
                matches = matches | queryset
            else:
                matches = queryset

        if matches:
            return matches.distinct()

        return queryset.distinct()


    def get_queryset(self):
        return self.get_query_queryset()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)


class FreelanceRetrieveAPIView(RetrieveAPIView):
    serializer_class = FreelancerDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        username = self.kwargs.get("username")
        freelancer = Freelancer.objects.filter(user__username=username).first()

        if not freelancer:
            return Response({"message": "This request is prohibited"}, status=403)

        serializer = self.get_serializer(freelancer)

        print(serializer.data)

        return Response(serializer.data, status=200)
