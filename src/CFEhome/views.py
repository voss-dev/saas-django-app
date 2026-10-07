from django.shortcuts import render
from visits.models import PageVisit
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

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
        "can_view_stats": request.user.has_perm("visits.view_pagevisit"),
    }        

    return render(request,  html_template, my_context)

@login_required
def user_only_view(request):
    return render(request, "protected/user_only.html")

@staff_member_required(login_url='/accounts/login')
def staff_only_view(request):
    return render(request, "protected/staff_only.html")