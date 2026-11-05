from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from subscriptions.models import UserSubscription

@login_required
def dashboard_view(request, *args, **kwargs):
    user_sub, created = UserSubscription.objects.get_or_create(user=request.user)

    context = {
        "user_sub": user_sub,
        "subscription": user_sub.subscription,
    }

    return render(request, "dashboard/main.html",  context)
