import datetime

import after_response
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from jobs.models.job import Job, JobAgentProxy

from .scrapper import G4SJobScraper, GamJobScraper

printTime = lambda x, y: print(f"\nTime taken: {y - x}\n\n")

scrapping = False


@after_response.enable
def scrape():
    global scrapping

    if scrapping:
        return

    scrapping = True
    start_time = datetime.datetime.now()

    scrapper = GamJobScraper(to_json=True)
    scrapped_jobs = scrapper.scrape()

    proxy = JobAgentProxy()
    proxy.save_scraped_jobs(scrapped_jobs)

    end_time = datetime.datetime.now()
    printTime(start_time, end_time)

    scrapping = False


@login_required
def index(request: HttpRequest):
    if not request.user.is_staff:
        return HttpResponse("403 Forbidden request!")

    scrape.after_response()
    return HttpResponse("<h1>Scrapping in process</h1>")
