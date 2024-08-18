import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpRequest, JsonResponse

from core.models import Waitlist

frontend_url = os.environ.get("FRONTEND_URL")

global_context = {
    "waitlist_cookie": False,
    "frontend_url": frontend_url,
}


def index(request: HttpRequest):
    subscriber_cookies = request.COOKIES.get("subscriber")
    subscriber = Waitlist.objects.filter(email=subscriber_cookies).first()
    if subscriber:
        global_context["subscriber"] = subscriber
    else:
        global_context["subscriber"] = None
    return render(request, "core/index.html", global_context)


def health(request: HttpRequest):
    try:
        Waitlist.objects.first()
        return JsonResponse(
            {"status": "OK", "message": "Backend Web-server up and running"}
        )
    except Exception as e:
        return JsonResponse({"status": "ERROR", "message": str(e)}, status=400)


def status(request: HttpRequest):
    return JsonResponse(
        {"status": "OK", "message": "Backend Web-server up and running"}
    )


def waitlist(request: HttpRequest):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        try:
            subscriber = Waitlist.objects.get(email=email)
            messages.success(request, "You are already in our waitlist, Thank You!")
        except Waitlist.DoesNotExist:
            subscriber = Waitlist(name=name, email=email)
            subscriber.save()
        except:
            messages.success(request, "Thank you for joining our waiting list")
            messages.error(request, "Something went wrong")

        response = redirect("index", permanent=True)
        response.set_cookie("subscriber", subscriber.email)
        return render(request, "core/index.html", global_context)

    return HttpResponseRedirect("/")
