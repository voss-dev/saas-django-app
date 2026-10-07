# Control how existing models appear in Django Admin

from django.contrib import admin
from .models import Subscription, SubscriptionPrice
# Register your models here.

# Defines an inline admin layout for SubscriptionPrice
class SubscriptionPriceInline(admin.TabularInline):
    model = SubscriptionPrice #Telling Django which model appears inside the Subscription admin page
    extra = 0 #Does not show extra empty forms for creating prices
    readonly_fields = ['stripe_id'] #Displays stripe_id, but prevents editing it in the admin


# Registers Subscription with the admin and customizes its admin page
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin): #SubscriptionAdmin is tied to 'Subscription' model
    
    # Shows related SubscriptionPrice records on the same subscription page. This works because SubscriptionPrice has a relationship to Subscription
    inlines = [SubscriptionPriceInline]

    # Displays those fields as columns in the Subscription list page
    list_display = ['name', 'active']
