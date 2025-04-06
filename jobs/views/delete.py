from django.db import transaction
from django.http import HttpRequest
from rest_framework import serializers
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response

from contracts.models.contract import Contract
from core.services.logger.main import DokoolaLoggerService
from jobs.models import Job
from jobs.models.job import JobStatusChoices
from projects.models import Milestone, Project
from proposals.models import Proposal
from users.models.user import User
from utilities.generator import get_serializer_error_message


class ThirdPartyJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "status",
            "published",
        ]


class JobDeleteAPIView(DestroyAPIView):

    def get_client_id(self, request):
        user: User = request.user

        client, profile_name = user.profile

        if profile_name.lower() != "client":
            raise ValueError("Forbidden Request")

        return client.public_id

    def get_queryset(self, public_id: str, client_id: str):
        queryset = Job.objects.get(public_id=public_id)
        if queryset.client.public_id != client_id:
            raise Job.DoesNotExist("This job does not exist")
        return queryset

    def delete(self, request: HttpRequest, public_id):

        try:
            with transaction.atomic():
                client_id = self.get_client_id(request)
                job = self.get_queryset(public_id, client_id)
                termination_message = f"We're sorry to inform you that the Job <strong>{job.title}</strong> has been deleted by the client"

                if not job:
                    return Response(
                        {
                            "message": "This is a Forbidden request",
                        },
                        status=403,
                    )

                proposals = Proposal.objects.filter(
                    job=job, status__in=Proposal._active_statuses()
                )
                for proposal in proposals:
                    proposal._terminate(commit_save=False, reason=termination_message)

                projects = []
                milestones = []

                contracts = Contract.objects.filter(
                    job=job, status__in=Contract._active_statuses()
                )
                for contract in contracts:
                    contract._terminate(commit_save=False, reason=termination_message)
                    _projects = Project.objects.filter(
                        contract=contract, status__in=Project._active_statuses()
                    )

                    if _projects.exists():
                        project = _projects.first()
                        if not project:
                            continue
                        project._terminate(
                            commit_save=False, reason=termination_message
                        )
                        projects.append(project)

                        _milestones = project.milestones.filter()

                        for milestone in _milestones:
                            milestone._terminate(termination_message)
                            milestones.append(milestone)

                job.status = JobStatusChoices.DELETED
                job.published = False
                job.is_valid = False
                job.is_deleted = True
                job.save()

                if milestones:
                    Milestone.objects.bulk_update(
                        milestones, fields=["status", "client_comment"]
                    )

                if projects:
                    Project.objects.bulk_update(projects, fields=["status", "termination_comment"])

                if contracts:
                    Contract.objects.bulk_update(contracts, fields=["status", "client_comment"])

                if proposals:
                    Proposal.objects.bulk_update(proposals, fields=["status", "client_comment"])

            return Response(
                {"message": "Job deleted successfully"},
                status=201,
            )
        except Job.DoesNotExist as e:
            DokoolaLoggerService.error(
                str(e),
                {
                    "public_id": public_id,
                    "client_id": client_id,
                    "user_id": request.user.pk,
                    "view_handler": self.__class__.__name__,
                    "request_id": request.session.__str__(),
                },
            )
            return Response(
                {"message": "Job not found"},
                status=404,
            )
        except Exception as e:
            DokoolaLoggerService.error(
                e,
                {
                    "public_id": public_id,
                    "client_id": client_id,
                    "user_id": request.user.pk,
                    "view_handler": self.__class__.__name__,
                    "request_id": request.session.__str__(),
                },
            )
            return Response(
                {"message": "This request is forbidden"},
                status=403,
            )
