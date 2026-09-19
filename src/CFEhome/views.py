from django.shortcuts import render
from visits.models import PageVisit

# Create your views here.
def home_view(request, *args, **kwargs):
    return about_view(request, *args, **kwargs)

def about_view(request, *args, **kwargs):
    # Creating a new PageVisit entry in the database
    PageVisit.objects.create(path=request.path)

    # 2.Query all visit and path_specific visits
    total_qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)

    # 3.Calculating the percentage of traffic for this specific visits
    try:
        percent = (page_qs.count() * 100.0) / total_qs.count()
    except ZeroDivisionError:
        percent = 0.0

    my_title = "My Page"
    
    
    html_template = "home.html"

    my_context = {
        "page_title": my_title,
        "page_visit_count": page_qs.count(),
        "total_visit_count": total_qs.count(),
        "percent": percent,
    }        

    return render(request,  html_template, my_context)