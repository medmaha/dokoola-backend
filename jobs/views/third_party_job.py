from django.db import transaction
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from jobs.models import Job
from jobs.models.job import JobStatusChoices
from proposals.models import Proposal, ProposalStatusChoices
from utilities.generator import get_serializer_error_message


class ThirdPartyJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "status",
            "published",
        ]


class ThirdPartyJobAPIView(GenericAPIView):
    """
    API view for managing third-party job listings.

    Allows clients to update the status and publication state of their third-party job postings.
    Requires client authentication and validates that the requesting user has appropriate permissions.
    """

    serializer_class = ThirdPartyJobSerializer

    def get_serializer(self, *args, **kwargs) -> ThirdPartyJobSerializer:
        return self.serializer_class(*args, **kwargs)

    def get_queryset(self, public_id: str, client_id: str|None=None):
        if client_id:
            queryset = Job.objects.only(
                "id",
                "client__public_id",
                "published",
                "status",
                "public_id",
                "is_third_party",
            ).get(client__public_id=client_id, public_id=public_id, is_third_party=True)
        else:
            queryset = Job.objects.only(
                "id",
                "client__public_id",
                "published",
                "status",
                "public_id",
                "is_third_party",
            ).get(public_id=public_id, is_third_party=True)
        return queryset

    def put(self, request, public_id):
        try:
            profile, profile_type = request.user.profile
            is_applied = profile_type == "Talent" and "applied" in request.data

            with transaction.atomic():
                job = self.get_queryset(public_id, profile.public_id if not is_applied else None)

                if is_applied:
                    Proposal.objects.get_or_create(
                        talent=profile,
                        job=job,
                        defaults={
                            "cover_letter":"N/A",
                            "duration": job.estimated_duration,
                            "client_comment": "External",
                            "status": ProposalStatusChoices.EXTERNAL,
                            "budget": job.pricing.get("budget") if job.pricing else 0.00,
                        }
                    )
                    return Response(status=204)

                serializer = self.get_serializer(data=request.data, instance=job)

                if serializer.is_valid():
                    serializer.save(status=JobStatusChoices.CLOSED)
                    return Response(
                        status=204,
                    )

                else:
                    return Response(
                        {"message": get_serializer_error_message(serializer.errors)},
                        status=400,
                    )

        except Job.DoesNotExist:
            return Response(
                {"message": "Job not found"},
                status=404,
            )
        
        except Exception as e:
            return Response(
                {"message": "This request is forbidden"},
                status=403,
            )
