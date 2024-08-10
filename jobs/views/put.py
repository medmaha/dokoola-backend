from rest_framework.generics import (
    UpdateAPIView,
)
from django.db.models import Q
from rest_framework.response import Response
from core.models import Category

from jobs.models import Job

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
