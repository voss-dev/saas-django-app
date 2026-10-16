from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subscriptions.models import (SubscriptionPrice, UserSubscription,)
from helpers.billing import (create_checkout_session, get_subscription, get_checkout_session)
from customers.models import Customer
# from django.utils import timezone
import datetime


# Create your views here.
# price_id
# # 5
# price_obj
# # SubscriptionPrice object with id=5
# price_obj.stripe_id
# # "price_monthly_123"
# request.user
# # User object for Alice
# user.customer.stripe_id
# # "cus_ABC123"
# success_url
# # "http://localhost:8000/checkout/success/?session_id={CHECKOUT_SESSION_ID}"
# cancel_url
# # "http://localhost:8000/pricing/"
# checkout_url
# # "https://checkout.stripe.com/c/pay/cs_test_abc123"

@login_required
def checkout_redirect_view(request, price_id=None):
    price_obj = SubscriptionPrice.objects.get(id=price_id)
    user = request.user
    customer_stripe_id = user.customer.stripe_id

    # Dynamic return URLs containing session_id placeholder for verification
    success_url = request.build_absolute_uri(f"/checkout/success/?session_id={{CHECKOUT_SESSION_ID}}")
    cancel_url = request.build_absolute_uri("/pricing/")

    # Generate Stripe Checkout URL
    checkout_url = create_checkout_session(
        customer_id=customer_stripe_id,
        price_id=price_obj.stripe_id,
        success_url=success_url,
        cancel_url=cancel_url
    )
    # http://localhost:8000/checkout/5/
    #     ↓
    # https://checkout.stripe.com/c/pay/cs_test_abc123
    #     ↓ successful payment
    # http://localhost:8000/checkout/success/?session_id=cs_test_abc123
    return redirect(checkout_url)

@login_required
def checkout_finalize_view(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect('/pricing/')

    # 1. Fetch session from Stripe
    checkout_session = get_checkout_session(session_id)

    # verifying that this is actually a subscription Checkout Session
    if checkout_session.get("mode") != "subscription":
        return redirect("pricing")
    
    stripe_sub_id = checkout_session.get('subscription')
    if not stripe_sub_id:
        return redirect("pricing")

    # 2. Fetch Subscription details to get billing period dates
    sub_data = get_subscription(stripe_sub_id)

    # Convert UNIX timestamps to Python aware datetime objects
    current_period_start = datetime.datetime.fromtimestamp(
        sub_data["items"]["data"][0]["current_period_start"], 
        tz=datetime.timezone.utc
    )

    current_period_end = datetime.datetime.fromtimestamp(
        sub_data["items"]["data"][0]["current_period_end"], 
        tz=datetime.timezone.utc
    )

    # 3. Match line item price ID back to local Subscription model
    stripe_price_id = sub_data['items']['data'][0]['price']['id']
    price_obj = SubscriptionPrice.objects.get(stripe_id=stripe_price_id)

    # 4. Update or Create the user's UserSubscription record
    # Copying the verified Stripe subscription information into your local object
    user_sub, created = UserSubscription.objects.get_or_create(user=request.user)
    user_sub.subscription = price_obj.subscription
    user_sub.stripe_id = stripe_sub_id
    user_sub.active = sub_data.get("status") == "active"
    user_sub.current_period_start = current_period_start
    user_sub.current_period_end = current_period_end
    user_sub.save() #Triggers Django signals to update user Group permissions!, persist the changes

    return render(request, "checkouts/success.html", {
        "subscription": user_sub.subscription
    })

