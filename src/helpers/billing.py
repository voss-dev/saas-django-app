# BUILDING THE BILLING HELPER ENGINE

import stripe
from django.conf import settings

# Initialize the global API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_customer(email=None, metadata=None, raw=False):
    """Creates a Customer in Stripe and returns the APi response."""
    response = stripe.Customer.create(
        email=email,
        metadata=metadata or {}
    )

    if raw:
        return response

    return response.get("id")

def create_checkout_session(customer_id, price_id, success_url, cancel_url, raw=False):
    """Creates a Hosted Checkout Session for recurring subscriptions."""

    # Creates a Stripe Checkout Session which:
    #  - accepts card payments
    #  - charges for the selected price
    #  - sets quantity to 1
    #  - uses mode='subscription', so the payment recurs
    #  - redirects using the supplied success and cancel URLs

    response = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1.
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
    )


    # If raw=True, it returns the complete Stripe response object, including session details
    if raw:
        return response

    # If raw remains False, it returns only  the hosted checkout page URL which you can use to redirect the customer
    return response.url