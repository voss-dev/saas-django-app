# Creating classes that create the model definitions
# make migrations and migrate create or change the actual database tables
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# AUTH_USER_MODEL = "auth.User", does not retrieve a user or the actual model class,only applied to model relationship
User = settings.AUTH_USER_MODEL

# Model classes — each generally represents a database table.
# Fields — columns such as name, email, or active.
# Relationships — links such as ForeignKey and ManyToManyField.
# Model methods — custom behavior for the model.
# Metadata — options such as permissions, ordering, and table names.

# Create your models here.

class Subscription(models.Model):
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={
            "content_type__app_label": "subscriptions"
        }
    )

    class Meta:
        permissions = [
            ("basic_perm", "Basic Plan Permission"),
            ("pro_perm", "Pro Plan Permission"),
            ("advanced_perm", "Advanced Plan Permission"),
        ]

    # Return a human-readable represeantaion of the object
    def __str__(self):
        return self.name


class UserSubscriptionQuerySet(models.QuerySet):
    def active(self):
        """Filters for subscriptions flagged as active"""
        return self.filter(active=True)
    
    def by_range(self, days_start=0, days_end=30):
        """
        Filters subscription expiring between days_start and days_end from today
        Expands the window to start at 00:00:00 and end at 23:59:59.
        """

        now = timezone.now()
        start_date = (now + timedelta(days=days_start)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = (now + timedelta(days=days_end)).replace(hour=23, minute=59, second=59, microsecond=999999)

        return self.filter(
            current_period_end__gte=start_date,
            current_period_end__lte=end_date,
        )

    def by_days_left(self, days=0):
        """Filters subscriptions expiring exactly within a specific number of days."""
        return self.by_range(days_start=0, days_end=days)

class UserSubscriptionManager(models.Manager):
    def get_queryset(self):
        return UserSubscriptionQuerySet(self.model, using=self._db,)
    
    def active(self):
        return self.get_queryset().active()

    def by_range(self, days_start=0, days_end=30):
        return self.get_queryset().by_range(days_start=days_start, days_end=days_end)
    
class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #Links one user to one subscription model, user deleted the subscription record deleted
    subscription = models.ForeignKey(
        Subscription, # Database Relationship
        on_delete=models.SET_NULL,
        null=True, # If the 'Subscription' is deleted user subscription remains but the 'subscription' value becomes null
        blank=True
    )
    active = models.BooleanField(default=True)
    user_cancelled = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    # Attach the custom manager
    objects = UserSubscriptionManager()
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription}"

@receiver(post_save, sender=UserSubscription)
def user_sub_post_save(sender, instance, *args, **kwargs):
    # Gets the related User and Subscription
    user_sub_instance = instance
    user = user_sub_instance.user
    current_sub = user_sub_instance.subscription

    # 1. Gather all groups IDs associated with ALL subscriptions in the system
    all_sub_groups = Subscription.objects.all().values_list('groups__id', flat=True)
    all_sub_group_set = set(all_sub_groups)

    # 2. Get current group IDs in the user
    user_group_set = set(user.groups.all().values_list('id', flat=True))

    # 3. Remove existing subscription groups from user set (preserve custom groups)
    non_sub_groups = user_group_set - all_sub_group_set

    # 4. Add the newly selected subscription's groups (if active)
    target_group_ids = set()
    if current_sub and user_sub_instance.active:
        sub_group_ids = current_sub.groups.all().values_list('id', flat=True)
        target_group_ids = set(sub_group_ids)

    final_group_ids = list(non_sub_groups | target_group_ids)

    # 5. Apply updated group list to user
    user.groups.set(final_group_ids)

class SubscriptionPrice(models.Model):
    INTERVAL_CHOICES = [
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    ]

    # on_delete decides what happens when to SubscriptionPrice when the referenced 'Subscription' is deleted
    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.CASCADE, #if the "Subscription" is deleted the related 'SubscriptionPrice' is also deleted
        null=True
    )
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(
        max_length=120, #Allows upto 120 characters
        choices=INTERVAL_CHOICES, #Restricts values to predefined options
        default='month' #Uses 'month' if no value is provided
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)

    @property
    def stripe_price(self):
        #Stripe accepts prices in integer cents (e.g., $99.99 -> 9999)

        return int(self.price * 100)

    def __str__(self):
        return f"{self.subscription.name} - {self.interval} (${self.price})"
