import re

from django.db import transaction
from rest_framework.generics import (
    CreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from clients.models import Client
from jobs.models import Activities, Job, Pricing
from jobs.serializers import (
    JobCreateSerializer,
    JobListSerializer,
)
from users.models import User
from utilities.generator import get_serializer_error_message

from .utils import get_category


class JobCreateAPIView(CreateAPIView):

    serializer_class = JobCreateSerializer

    def create(self, request: Request, *args, **kwargs):
        try:

            user: User = request.user

            if not user.is_client:
                return Response(
                    {"message": "Talents can't create job openings"},
                    status=401,
                )

            profile, _ = user.profile

            if not user.is_client:
                return Response({"message": "This request is forbidden!"}, status=403)

            data: dict = request.data.copy()  # type: ignore

            category = get_category(data.pop("category", "None"))

            if not category:
                return Response({"message": "Invalid job category"}, status=400)

            serializer = self.get_serializer(data=data)

            with transaction.atomic():
                if serializer.is_valid():
                    job = serializer.save(
                        client=profile,
                        category=category,
                    )
                    Activities.objects.create(job=job)
                    return Response({"_id": job.pk}, status=201)

                message = get_serializer_error_message(serializer.errors)
                return Response({"message": message}, status=400)

        except Exception as e:
            return Response({"message": str(e)}, status=400)
