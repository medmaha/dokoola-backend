from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from clients.models import Client
from users.models import User

from rest_framework.permissions import IsAuthenticated

from .models import Activities, Job, Pricing
from .serializer import JobsDetailSerializer, JobsSerializer, JobsCreateSerializer
import re


class JobsListAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobsSerializer

    def get_queryset(self):
        queryset = Job.objects.filter(active_state=True)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)


class JobDetailAPIView(RetrieveAPIView):
    permission_classes = []
    serializer_class = JobsDetailSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]
        queryset = Job.objects.filter(slug=slug, active_state=True).first()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(self.get_queryset())
            return Response(serializer.data, status=200)

        return Response({"message':'Resources not found"}, status=404)


class JobCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobsCreateSerializer

    def get_serializer(self, *args, **kwargs) -> JobsCreateSerializer:
        return super().get_serializer(*args, **kwargs)

    def create(self, request: Request, *args, **kwargs):
        user: User = request.user

        client = Client.objects.filter(user=user).first()

        if not client:
            return Response(
                {"message": "Freelancers can't create job openings"}, status=401
            )

        data: dict = request.data.copy()  # type: ignore

        pricing_data = data["pricing"]
        del data["pricing"]

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            pricing = Pricing.objects.create(**pricing_data)
            activities = Activities.objects.create()
            job = Job.objects.create(
                **data, activities=activities, pricing=pricing, client=client
            )
            serializer = JobsDetailSerializer(instance=job)
            return Response({"slug": job.slug}, status=201)

        message = ""

        for error in serializer.errors.items():
            field, text = error[0], error[1][0]

            if re.search(rf"{field}", text, re.IGNORECASE):
                message = text.capitalize()
                break

            message = field.capitalize() + ": " + text
            break
        return Response({"message": message}, status=400)
