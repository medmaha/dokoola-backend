from django.db import transaction

from rest_framework.generics import (
    CreateAPIView,
)
from rest_framework.response import Response
from rest_framework.request import Request
from utilities.generator import get_serializer_error_message
from clients.models import Client
from users.models import User

from rest_framework.permissions import IsAuthenticated

from jobs.models import Activities, Job, Pricing
from jobs.serializers import (
    JobRetrieveSerializer,
    JobCreateSerializer,
)


import re
from .utils import get_category


class JobCreateAPIView(CreateAPIView):

    serializer_class = JobCreateSerializer

    def create(self, request: Request, *args, **kwargs):
        try:

            user: User = request.user

            if not user.is_client:
                return Response(
                    {"message": "Freelancers can't create job openings"}, status=401
                )

            profile, profile_name = user.profile

            data: dict = request.data.copy()  # type: ignore

            category = get_category(data.pop("category", "None"))

            if not category:
                return Response({"message": "Invalid job category"}, status=400)

            if "pricing" in data:
                pricing_data: dict = data.pop("pricing")
            else:
                return Response({"message": "Invalid pricing data"}, status=400)

            serializer = self.get_serializer(data=data)

            with transaction.atomic():

                if serializer.is_valid():
                    pricing = Pricing.objects.create(
                        **{
                            **pricing_data,
                            "fixed_price": bool(pricing_data.get("fixed_price")),
                            "negotiable_price": bool(
                                pricing_data.get("negotiable_price")
                            ),
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
                        **data,
                        activities=activities,
                        pricing=pricing,
                        client=profile,
                        category_obj=category,
                    )
                    serializer = JobRetrieveSerializer(instance=job)
                    return Response({"slug": job.slug}, status=201)

                message = get_serializer_error_message(serializer.errors)

                ("Error", message)
                return Response({"message": message}, status=400)

        except Exception as e:
            return Response({"message": str(e)}, status=400)
