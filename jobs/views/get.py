from random import shuffle

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from core.services.after.main import AfterResponseService
from jobs.models import Activities, Job
from jobs.models.job import JobStatusChoices
from jobs.serializers import (
    ActivitySerializer,
    JobListSerializer,
    JobRetrieveSerializer,
)
from jobs.serializers.retrieve import JobRelatedSerializer
from src.features.paginator import DokoolaPaginator
from users.models.user import User
from utilities.time import utc_datetime, utc_timestamp

active_statues = [
    JobStatusChoices.PUBLISHED,
    JobStatusChoices.COMPLETED,
    JobStatusChoices.IN_PROGRESS,
    # JobStatusChoices.SUSPENDED,
    # JobStatusChoices.CLOSED,
    # JobStatusChoices.DELETED
    # JobStatusChoices.CONTRACTED
]

guest_job_query = Q(is_valid=True, status__in=active_statues)


def client_job_query(user_id):
    return Q(
        client__user__pk=user_id,
        status__in=[
            *active_statues,
            JobStatusChoices.CLOSED,
            JobStatusChoices.DELETED,
            JobStatusChoices.PENDING,
            JobStatusChoices.CONTRACTED,
        ],
    )


class JobListAPIView(ListAPIView):
    permission_classes = []
    serializer_class = JobListSerializer

    def exclude_proposed_jobs(self, queryset, profile, profile_type):
        if profile and profile_type == "Talent":
            return queryset.exclude(public_id__in=profile.applications_ids)
        return queryset

    def get_queryset(self, user: User):
        profile, profile_type = (
            user.profile if hasattr(user, "public_id") else (None, "")
        )
        if user:
            query = guest_job_query & Q(published=True) | client_job_query(user.pk)
            queryset = Job.objects.filter(query)
        else:
            queryset = Job.objects.filter(
                guest_job_query,
                published=True,
            )

        queryset = self.exclude_proposed_jobs(queryset, profile, profile_type).order_by(
            "application_deadline", "-created_at", "published"
        )
        return queryset.select_related("category", "client__user", "client__company")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.user)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class JobRelatedAPIView(ListAPIView):
    serializer_class = JobRelatedSerializer

    def get_queryset(self, public_id=None):
        instance = get_object_or_404(Job, public_id=public_id)

        valid_job_query = (
            guest_job_query
            & Q(application_deadline__gte=utc_datetime(add_minutes=1))
            & Q(published=True)
        )

        job_type_query = Q(job_type=instance.job_type) | Q(
            job_type_other=instance.job_type_other
        )
        location_query = Q(address__contains=instance.address)
        # | Q(country__code=(instance.country or dict()).get("code"))
        category_query = Q(category=instance.category) | Q(
            category__parent=instance.category.parent if instance.category else None
        )
        experience_level_query = Q(experience_level=instance.experience_level) | Q(
            experience_level_other=instance.experience_level_other
        )

        # TODO: Filter out the jobs that user already applied to if user is a talent
        queryset = (
            Job.objects.filter(
                valid_job_query,
                Q(
                    category_query
                    | location_query
                    | job_type_query
                    | experience_level_query
                ),
            )
            .order_by("application_deadline", "pricing__budget", "client__rating")
            .exclude(pk=instance.pk)[:10]
        )

        if not queryset:
            queryset = (
                Job.objects.filter(valid_job_query, category_query)
                .order_by("application_deadline", "pricing__budget", "client__rating")
                .exclude(pk=instance.pk)[:5]
            )

        if not queryset:
            queryset = (
                Job.objects.filter(
                    job_type_query,
                )
                .order_by("application_deadline", "pricing__budget", "client__rating")
                .exclude(pk=instance.pk)[:5]
            )

        return queryset.select_related("client__user")

    def list(self, request, public_id: str):
        try:
            queryset = self.get_queryset(public_id)
            serializer = self.get_serializer(
                queryset, many=True, context={"request": "mini"}
            )
            data = [*serializer.data]
            shuffle(data)
            return Response(data[:6])
        except Exception as e:
            return Response({"message": "Internal Server Error"}, status=500)


class MyJobListPaginator(DokoolaPaginator):
    page_size = 10


class MyJobListAPIView(ListAPIView):
    serializer_class = JobListSerializer
    pagination_class = MyJobListPaginator

    def get_queryset(self):
        user_id = self.request.user.pk
        queryset = Job.objects.filter(client__user__pk=user_id).order_by("-updated_at")
        return queryset

    def list(self, request, *args, **kwargs):

        try:
            user: User = request.user
            if not user.is_client:
                return Response(
                    {"message": "403; Only clients can access this route"},
                    status=403,
                )

            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            # TODO: log error
            return Response(
                {"message": "Internal Server Error"},
                status=500,
            )


class JobRetrieveAPIView(RetrieveAPIView):
    serializer_class = JobRetrieveSerializer

    def update_last_client_visit_time(self, activity: Activities):
        client_last_visit = utc_datetime(add_minutes=2)
        activity.client_last_visit = client_last_visit
        activity.save()

    def get_queryset(self, public_id: str):
        user_id = self.request.user.pk
        query = guest_job_query | client_job_query(user_id)
        return Job.objects.select_related(
            "category", "client__company", "client__user", "activity"
        ).get(query, public_id=public_id)

    def retrieve(self, request, public_id, *args, **kwargs):
        try:
            instance = self.get_queryset(public_id)
            serializer = self.get_serializer(instance=instance)

            if instance.client.user.pk == request.user.pk:
                AfterResponseService.schedule_after(
                    self.update_last_client_visit_time, instance.activity
                )

            return Response(serializer.data, status=200)

        except Job.DoesNotExist:
            return Response({"message": "Resource not found"}, status=404)

        except Exception as e:
            print("============================================================")
            print(e)
            print("============================================================")
            return Response({"message": "Internal Server Error"}, status=500)


class JobActivitiesAPIView(GenericAPIView):
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
