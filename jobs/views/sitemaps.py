from django.utils.html import strip_tags
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from jobs.models import Job
from jobs.models.job import JobStatusChoices


class JobsSitemapAPIView(ListAPIView):
    permission_classes = []

    def list(self, *args, **kwargs):
        try:
            queryset = Job.objects.only("public_id", "updated_at").filter(
                is_valid=True,
                status=JobStatusChoices.PUBLISHED,
            ).order_by("-is_third_party", "-created_at", "pricing__budget").values("public_id", "updated_at")[:10]

            return Response(queryset, status=200)
        
        except Exception as e:
            return Response({"message": "Internal Server Error"}, status=500)
