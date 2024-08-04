from functools import partial
import threading
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    GenericAPIView,
)
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.request import Request
from core.models import Category
from clients.models import Client
from users.models import User

from rest_framework.permissions import IsAuthenticated

from .models import Activities, Job, Pricing
from .serializer import (
    JobsDetailSerializer,
    JobsActivitySerializer,
    JobsSerializer,
    JobsCreateSerializer,
    JobsUpdateSerializer,
)


import re
from django.utils import timezone


def get_category(slug:str):
    category = Category.objects.filter(Q(slug=slug)|Q(name=slug)).first()
    return category

class JobsListAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobsSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.filter(
            Q(is_valid=True, status="PUBLISHED") | Q(client__user=user)
        ).order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class JobUpdateAPIView(UpdateAPIView):
    permission_classes = []
    serializer_class = JobsUpdateSerializer

    def get_queryset(self, slug: str) -> Job | None:
        try:
            return Job.objects.get(slug=slug, is_valid=True)
        except:
            return None

    def update(self, request, *args, **kwargs) -> Response:

        data: dict = request.data

        instance = self.get_queryset(data.get("slug", ""))

        if not instance:
            return Response({"message": "Job not found"}, status=404)
        
        category = get_category(data.pop("category", "None")) or instance.category_obj
        if not category:
            return Response({"message": "Invalid job category"}, status=400) 
            
        serializer = self.get_serializer(
            instance=instance, data=data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(category_obj=category)
            return Response({"message": "Job updated successfully"}, status=200)

        return Response({"message": "Failed to update job"}, status=404)


class JobDetailAPIView(RetrieveAPIView):
    permission_classes = []
    serializer_class = JobsDetailSerializer

    def update_last_client_visit(self, activity: Activities) -> None:
        activity.client_last_visit = timezone.now()
        activity.save()

    def get_queryset(self):
        slug = self.kwargs["slug"]
        try:
            return Job.objects.get(slug=slug)
        except:
            return None

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(instance=queryset)

            if queryset.client.user.pk == request.user.pk:
                threading.Thread(
                    target=partial(self.update_last_client_visit, queryset.activities)
                ).start()

            return Response(serializer.data, status=200)

        return Response({"message':'Resources not found"}, status=404)


class JobActivitiesAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = JobsActivitySerializer

    def get_queryset(self, slug: str):
        try:
            queryset = Activities.objects.get(job__slug=slug)
            return queryset
        except Activities.DoesNotExist:
            return None

    def get(self, request, slug, **kwargs):
        queryset = self.get_queryset(slug)
        if queryset:
            serializer = self.get_serializer(instance=queryset)
            return Response(serializer.data, status=200)
        return Response({"message": "Error! Resources not found"}, status=404)


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

        category = get_category(data.pop("category", "None"))

        if not category:
            return Response({"message": "Invalid job category"}, status=400) 

        if "pricing" in data:
            pricing_data: dict = data.pop("pricing")
        else:
            return Response({"message": "Invalid pricing data"}, status=400) 

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            pricing = Pricing.objects.create(
                **{
                    **pricing_data,
                    "fixed_price": bool(pricing_data.get("fixed_price")),
                    "negotiable_price": bool(pricing_data.get("negotiable_price")),
                    "will_pay_more": bool(pricing_data.get("will_pay_more")),
                }
            )
            activities = Activities.objects.create()

            # TODO: fix this
            try:
                del data["job_type"]  # because it's not in the model
            except:
                pass

            job = Job.objects.create(
                **data, activities=activities, pricing=pricing, client=client, category_obj=category
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
