import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Category, Waitlist

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


class CategoriesView(APIView):
    permission_classes = []
    def get(self, request):
        categories = Category.objects.filter(disabled=False).values("slug", "name", "image_url", "description")
        return Response(categories)