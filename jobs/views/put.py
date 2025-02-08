from django.db.models import Q
from rest_framework.generics import (
    UpdateAPIView,
)
from rest_framework.response import Response

from core.models import Category
from jobs.models import Job
from jobs.models.job import JobStatusChoices
from jobs.serializers import (
    JobUpdateSerializer,
)


def get_category(slug: str):
    category = Category.objects.filter(Q(slug=slug) | Q(name=slug)).first()
    return category


class JobUpdateAPIView(UpdateAPIView):
    permission_classes = []
    serializer_class = JobUpdateSerializer

    def get_queryset(self, slug: str) -> Job | None:
        try:
            return Job.objects.get(id=slug, is_valid=True)
        except:
            return None

    def update(self, request, job_id, *args, **kwargs) -> Response:

        data: dict = request.data

        instance = self.get_queryset(job_id)

        if not instance:
            return Response({"message": "Job not found"}, status=404)

        if instance.proposal_count > 0:
            return Response({"message": "Job already in progress"}, status=400)

        if "published" in request.query_params:
            published = data.get("published", False) == True
            if published:
                status = JobStatusChoices.PUBLISHED
            else:
                status = JobStatusChoices.CLOSED

            instance.status = status
            instance.published = published
            instance.save()
            return Response(
                {
                    "message": "Job updated successfully",
                    "data": {"published": instance.published},
                },
                status=200,
            )

        category = get_category(data.pop("category", "None")) or instance.category

        if not category:
            return Response({"message": "Invalid job category"}, status=400)

        serializer = self.get_serializer(
            instance=instance,
            data=data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            status = instance.status
            if "published" in data:
                if data["published"]:
                    status = JobStatusChoices.PUBLISHED
                else:
                    status = JobStatusChoices.CLOSED

            serializer.save(category=category, status=status)
            return Response({"message": "Job updated successfully"}, status=200)

        return Response({"message": "Failed to update job"}, status=404)
