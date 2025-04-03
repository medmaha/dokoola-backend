import datetime
import logging
from typing import List

import after_response
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from jobs.models.job import Job, JobAgentProxy

logger = logging.getLogger(__name__)


def is_admin(user: AbstractUser):
    # if not hasattr(user, "is_authenticated"): return False
    # if not user.is_authenticated: return False
    # return user.is_staff

    return True


@user_passes_test(is_admin)
def index(request: HttpRequest):
    global time_remaining

    print(logger.info("Route hit"))

    if not check_is_scraping():
        # Call the function after the response is sentt

        _site: JobAgentProxy.SITE = str(request.GET.get("site", "")).lower()
        if _site and not _site in JobAgentProxy.SITES:
            _site = None

        if not _site:
            _site = "gamjobs"

        _max_jobs = str(request.GET.get("jobs", ""))
        if _max_jobs and _max_jobs.isdigit():
            _max_jobs = int(_max_jobs)
        elif _max_jobs:
            _max_jobs = None

        do_scrape.after_response(site=_site, max_jobs=_max_jobs)

        return HttpResponse("<h1>Scrapping in process</h1>")

    return HttpResponse(
        "<h1 style='color:red;'>{}</h1>".format(
            time_remaining or "Error: Scrapping in process"
        ),
        status=403,
    )


@user_passes_test(is_admin)
def invalidate_jobs(request: HttpRequest):

    today = timezone.now()
    last_name = today - datetime.timedelta(days=30)

    invalid_jobs = (
        Job.objects.only("id")
        .filter(
            is_valid=True,
            published=True,
            is_third_party=True,
            application_deadline__lt=today,
        )
        .values_list("id", flat=True)
    )

    if len(invalid_jobs):
        do_invalidation.after_response(invalid_jobs)

    response = HttpResponse(
        '{"success": true, "message": "Jobs invalidated", "jobs_count": '
        + str(len(invalid_jobs))
        + "}"
    )
    response.headers["content-type"] = "application/json"
    return response


is_deleting = False
is_scrapping = False
time_remaining = ""
last_scraped_time = None


def check_is_scraping():

    global last_scraped_time, time_remaining

    now = datetime.datetime.now()
    if last_scraped_time is None:
        return False

    time_difference = now - last_scraped_time
    restriction_expired = (
        time_difference.total_seconds() > 300
    )  # 5 minutes = 300 seconds

    if not restriction_expired:
        last_scraped_time = None
        time_remaining = f"{5 - int(time_difference.total_seconds() / 60)} minutes remaining until next scrape"

    return restriction_expired


@after_response.enable
def do_invalidation(job_ids: List[int]):
    Job.objects.only("id").filter(id__in=job_ids).delete()


@after_response.enable
def do_scrape(site: JobAgentProxy.SITE, max_jobs=None):
    logger.info("Doing Scraping")
    global is_scrapping
    if check_is_scraping():
        return
    try:
        is_scrapping = True
        proxy = JobAgentProxy()
        proxy.scrape_site(site=site, max_jobs=max_jobs)
        last_scraped_time = datetime.datetime.now()
    except Exception as e:
        logger.error(e)
