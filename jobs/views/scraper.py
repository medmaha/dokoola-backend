from django.db import transaction
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from clients.models import Client
from core.models import Category
from jobs.models.activities import Activities
from jobs.models.job import Job, JobStatusChoices
from utilities.generator import primary_key_generator, public_id_generator


class JobScrapperAPIView(ListAPIView):
    """
    API view to handle job scraping from third-party sources.
    """

    permission_classes = []

    def verify_source(self, request) -> bool:
        """
        Verifies the source of the request to ensure it is authorized.
        """
        return True

    def post(self, request, *args, **kwargs):
        try:
            # Verify the source of the request
            # If the source is not verified, return a 403
            verified_source = self.verify_source(request)
            if not verified_source:
                return Response({"message": "403: Forbidden request"}, status=403)

            # Extract the site and job data from the request
            _site: list[dict] = request.data.get("site", "")
            _data: list[dict] = request.data.get("third_party_jobs", [])

            if not _data:
                return Response({"message": "No jobs found"}, status=400)

            # Collect third-party job addresses from the provided data
            job_addresses = [
                job_data.get("third_party_address", "") for job_data in _data
            ]

            # Fetch existing jobs with matching third-party addresses
            existing_jobs = set(
                Job.objects.only("third_party_address")
                .filter(third_party_address__in=job_addresses)
                .values_list("third_party_address", flat=True)
            )

            client = Client.objects.get(is_agent=True)
            category = Category.objects.get(is_agent=True)

            if _site == "gamjobs":
                published = True
                status = JobStatusChoices.PUBLISHED
            else:
                published = False
                status = JobStatusChoices.DRAFT

            # Filter out jobs that already exist and prepare new job objects
            filtered_jobs = []
            activities = []
            for job_data in _data:
                third_party_address = job_data.get("third_party_address")
                if third_party_address and third_party_address not in existing_jobs:
                    _id = primary_key_generator()
                    self.public_id = public_id_generator(_id, Job.PUBLIC_ID_PREFIX)
                    try:
                        job = Job(
                            **job_data,
                            id=_id,
                            status=status,
                            client=client,
                            category=category,
                            published=published,
                            public_id=self.public_id,
                        )
                        job.full_clean()
                        filtered_jobs.append(job)

                        # Create an activity for each new job
                        activity = Activities(
                            job=job, public_id=public_id_generator(_id, "ATV")
                        )
                        activity.clean()
                        activities.append(activity)
                    except Exception as e:
                        print("ERROR:", e)

            # Use a database transaction to bulk create the new jobs
            with transaction.atomic():
                jobs = Job.objects.bulk_create(filtered_jobs)
                Activities.objects.bulk_create(activities)
                return Response(
                    {"message": "Jobs created successfully", "count": len(jobs)},
                    status=200,
                )

        except Exception as e:
            # TODO: log error
            print("Error:", e)
            return Response({"message": str(e)}, status=500)
