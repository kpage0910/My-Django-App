from django.shortcuts import render
from datetime import datetime
from .models import Course


def getISMCourses():
    return [
        Course("ISM 671", "Organizing Data for Analytics"),
        Course("ISM 672", "App Design and Programming"),
        Course("ISM 673", "Designing Secure Networks"),
    ]


def getFormattedDateTime():
    return datetime.today().strftime("%A %B %d, %Y")


def home(request):
    ISMCourses = getISMCourses()
    timeNow = getFormattedDateTime()
    return render(
        request=request,
        template_name="myapp/home.html",
        context={"today": timeNow, "ISMCourses": ISMCourses, "title": "My Django App"},
    )
