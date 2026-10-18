from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from subscriptions.models import UserSubscription
from helpers.billing import get_subscription

class Command(BaseCommand):
    help = "Syncs active user subscriptions with Stripe billing status"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days-left",
            type=int,
            default=0,
            help="Filter Subscription ending within this many days",
        )

    def handle(self, *args, **options):
        days_left = options.get("days_left")

        # 1. Query subscriptions expiring soon using our custom QuerySet
        qs = UserSubscription.objects.filter(stripe_id__isnull=False)
        if days_left > 0:
            qs = qs.by_days_left(days=days_left)

        self.stdout.write(f"Checking {qs.count()} subscription records against Stripe...")

        # qs = [Alice, Brian, David]
        for user_sub in qs:
            try:
                # 2. Query the Stripe API for current status
                sub_data = get_subscription(user_sub.stripe_id)
                status = sub_data.status

                subscription_item = sub_data["items"]["data"][0]
                # 3.Update period timestamps
                current_period_start = datetime.datetime.fromtimestamp(subscription_item["current_period_start"], tz=datetime.timezone.utc)
                current_period_end = datetime.datetime.fromtimestamp(subscription_item["current_period_end"], tz=datetime.timezone.utc)

                user_sub.current_period_start = current_period_start
                user_sub.current_period_end = current_period_end
                user_sub.active = status == "active"
                # user_sub.save(update_fields=["current_period_start", "current_period_end", "active"])

                self.stdout.write(self.style.SUCCESS(f"Synced {user_sub.user.username}: status={status}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error syncing {user_sub.user.username}: {e}"))