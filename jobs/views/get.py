from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from core.services.after.main import AfterResponseService
from jobs.models import Activities, Job
from jobs.models.job import JobStatusChoices
from jobs.serializers import (
    ActivitySerializer,
    JobListSerializer,
    JobRetrieveSerializer,
)
from users.models.user import User
from utilities.generator import public_id_generator


class JobListAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobListSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        if user_id:
            queryset = (
                Job.objects.filter(
                    # Q(is_valid=True, status=JobStatusChoices.PUBLISHED)
                    Q(is_valid=True)
                    | Q(client__user__pk=user_id)
                )
                .select_related("client", "category")
                .order_by("-created_at", "published")
            )
            return queryset
        else:
            queryset = Job.objects.filter(Q(is_valid=True)).order_by(
                "-created_at", "published"
            )

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
                {"message": "Only clients can access this route"},
                status=403,
            )

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class JobRetrieveAPIView(RetrieveAPIView):
    permission_classes = []
    serializer_class = JobRetrieveSerializer

    def get_queryset(self, public_id: str):
        try:
            print("Job ID:",public_id)
            # Job.objects.filter(is_third_party=True).update(status=JobStatusChoices.PUBLISHED)
            return Job.objects.get(public_id=public_id)
        except Exception as e:
            print("Error:",e)
            return None

    def update_last_visit(self, job: Job):
        job.activities.client_last_visit = timezone.now()
        job.activities.save()

    def retrieve(self, request, public_id, *args, **kwargs):
        instance = self.get_queryset(public_id)
        if instance:
            serializer = self.get_serializer(instance=instance)

            # for j in Job.objects.filter():
            #     j.public_id = public_id_generator(j.id, "job")
            #     print("Job ID: ",j.id,"Public ID: ",j.public_id)
            #     j.save()

            if instance.client.user.pk == request.user.pk:
                AfterResponseService.register(self.update_last_visit, instance)
            return Response(serializer.data, status=200)

        return Response({"message':'Resources not found"}, status=404)


class JobActivitiesAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = ActivitySerializer

    def get_queryset(self, public_id: str):
        try:
            queryset = Activities.objects.select_related("job").get(
                job__public_id=public_id
            )
            return queryset
        except Activities.DoesNotExist:
            return None

    def get(self, request, public_id, **kwargs):
        queryset = self.get_queryset(public_id)

        if queryset:
            serializer = self.get_serializer(instance=queryset)
            return Response(serializer.data, status=200)
        return Response({"message": "Error! Resources not found"}, status=404)
