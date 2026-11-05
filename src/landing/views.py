from django.shortcuts import render

from visits.models import PageVisit
from helpers.numbers import short_number
from dashboard.views import dashboard_view

# Create your views here.
def landing_page_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return dashboard_view(request, *args, **kwargs)

    PageVisit.objects.create(path=request.path)

    total_qs = PageVisit.objects.all()
    page_views_count = total_qs.count()

    context = {
        "page_views_count": page_views_count,
        "page_views_formatted": short_number(page_views_count * 1000),
    }

    return render(request, "landing/main.html", context)