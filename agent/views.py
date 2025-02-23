from django.http import JsonResponse

from jobs.models.job import Job, JobAgentProxy
from .scrapper import GamJobScraper, G4SJobScraper
import datetime

printTime = lambda x, y: print(f"\n\nTime taken: {y - x}\n\n")


def index(request):

    # Job.objects.filter(is_third_party=True).delete()
    start_time = datetime.datetime.now()

    scrapper = GamJobScraper(to_json=True)
    jobs = scrapper.scrape()

    proxy = JobAgentProxy()
    proxy.save_scraped_jobs(jobs)

    end_time = datetime.datetime.now()
    printTime(start_time, end_time)

    return JsonResponse(
        jobs,
        safe=False,
    )
