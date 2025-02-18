from django.http import JsonResponse
from .scrapper import GamJobScraper
import datetime

printTime = lambda x, y : print(f"\n\nTime taken: {y - x}\n\n")


def index(request):

    start_time = datetime.datetime.now()

    jobs = GamJobScraper.scrape()

    end_time = datetime.datetime.now()
    printTime(start_time, end_time)

    return JsonResponse(jobs, safe=False)




