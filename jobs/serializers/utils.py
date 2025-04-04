from jobs.models import Job
from proposals.models import Proposal
from users.models import User


def check_has_proposed(context: dict, instance: Job):
    """A utility function to check if the user has proposed to the job"""
    request = context.get("request")
    user: User | None = request.user if request else None

    if user and user.is_authenticated and user.is_talent:

        # Check if the user has proposed to the job
        has_proposed = (
            Proposal.objects.select_related()
            .filter(job=instance, talent__user=user)
            .exists()
        )

        # return a boolean value
        return has_proposed

    return False
