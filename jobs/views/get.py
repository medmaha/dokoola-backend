from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    GenericAPIView,
)
from django.db.models import Q
from rest_framework.response import Response


from users.models.user import User
from jobs.models import Activities, Job, JobStatusChoices
from jobs.serializers import (
    JobRetrieveSerializer,
    ActivitySerializer,
    JobListSerializer,
    JobListSerializer,
)
from django.utils import timezone

import after_response


class JobListAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobListSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        if user_id:
            queryset = Job.objects.filter(
                # Q(is_valid=True, status=JobStatusChoices.PUBLISHED)
                Q(is_valid=True)
                | Q(client__user__pk=user_id)
            ).order_by("-created_at")
            return queryset
        else:
            queryset = Job.objects.filter(Q(is_valid=True)).order_by("-created_at")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class MyJobListAPIView(ListAPIView):
    serializer_class = JobListSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        queryset = Job.objects.filter(client__user__pk=user_id).order_by("-created_at")
        return queryset

    def list(self, request, *args, **kwargs):

        user: User = request.user

        if not user.is_client:
            return Response(
                {"message": "Only clients can access this route"}, status=403
            )

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class JobRetrieveAPIView(RetrieveAPIView):
    permission_classes = []
    serializer_class = JobRetrieveSerializer

    def get_queryset(self, job_id: str):
        try:
            return Job.objects.get(pk=job_id)
        except:
            return None

    def retrieve(self, request, job_id, *args, **kwargs):
        queryset = self.get_queryset(job_id)
        if queryset:
            serializer = self.get_serializer(instance=queryset)

            if queryset.client.user.pk == request.user.pk:

                # FIXME: optimize for better performance
                queryset.activities.client_last_visit = timezone.now()
                queryset.activities.save()

            return Response(serializer.data, status=200)

        return Response({"message':'Resources not found"}, status=404)


class JobActivitiesAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = ActivitySerializer

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
