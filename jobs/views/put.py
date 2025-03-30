from django.db import transaction
from django.db.models import Q
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from core.models import Category
from jobs.models import Job
from jobs.models.job import JobStatusChoices
from jobs.serializers import JobUpdateSerializer
from utilities.generator import get_serializer_error_message


def get_category(slug: str):
    category = Category.objects.filter(Q(slug=slug) | Q(name=slug)).first()
    return category


class JobUpdateAPIView(UpdateAPIView):
    permission_classes = []
    serializer_class = JobUpdateSerializer

    def check_can_publish(self, job: Job):
        return job.status in [
            JobStatusChoices.PUBLISHED,
            JobStatusChoices.PENDING,
            JobStatusChoices.CLOSED,
        ]

    def update(self, request, public_id):

        data: dict = request.data

        try:
            with transaction.atomic():

                instance = Job.objects.select_for_update().get(public_id=public_id)

                assert (
                    instance.client.public_id == request.user.public_id
                ), "403: Forbidden request!"

                if "published" in request.query_params:

                    if not self.check_can_publish(instance):
                        return Response(
                            {"message": "This action is forbidden"}, status=403
                        )

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
                            "data": {"published": instance.published, "_id": public_id},
                        },
                        status=200,
                    )

                category = (
                    get_category(data.pop("category", "None")) or instance.category
                )

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

                error_msg = get_serializer_error_message(
                    serializer.errors, default_message="Failed to update job"
                )
                return Response({"message": error_msg}, status=404)

        except Job.DoesNotExist as e:
            return Response({"message": "Job not found"}, status=404)

        except AssertionError as e:
            return Response({"message": str(e)}, status=403)

        except:
            pass
