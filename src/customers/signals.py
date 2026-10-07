# Automatic Customer Creation with Allauth Signals


# 1. User confirms email
# 2. email_confirmed signal free
# 3. find or create local Customer
# 4. Create Stripe Customer if stripe_id is missing
# 5. Save Stripe ID locally

from django.dispatch import  receiver #Django receiver decorator, connects a function to a signal
from allauth.account.signals import user_signed_up, email_confirmed #Imports Allauth's signal that fires when a user confirms their email
from .models import Customer
from helpers.billing import create_stripe_customer

# @receiver(email_confirmed) registers the function as a listener for Allauth's signal.
# When a user confirms their email, Allauth sends that signal, and Django automatically calls this function
@receiver(email_confirmed)
def allauth_email_confirmed_handler(request, email_address, *args, **kwargs):
    user = email_address.user  #Getting the User object related to the confirmed email

    # Get or create local Customer object
    customer_obj, created = Customer.objects.get_or_create(user=user) #finds or creates a Customer database record
    customer_obj.init_email = email_address.email
    customer_obj.init_email_confirmed = True

    # Create Customer on Stripe if missing
    if not customer_obj.stripe_id:
        stripe_id = create_stripe_customer(
            email=email_address.email,
            metadata={"user_id": user.id, "username": user.username}
        )

        customer_obj.stripe_id = stripe_id

    customer_obj.save()
