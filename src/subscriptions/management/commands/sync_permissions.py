from django.core.management.base import BaseCommand
from subscriptions.models import Subscription

class Command(BaseCommand): #defines the custom command
    help = "Syncs subscription permissions across all associated Django Groups"

    def handle(self, *args, **options): #contains the command main logic
        self.stdout.write("Syncing subscription permissions...")

        subscriptions = Subscription.objects.filter(active=True) #stores the resulting QuerySet, [Basic, Pro]
        for sub in subscriptions: #processes each active subscription
            sub_perms = sub.permissions.all() #gets that subscription's permissions
            for group in sub.groups.all():
                # Assign subscription permissions to the connected group
                group.permissions.set(sub_perms)

        self.stdout.write(self.style.SUCCESS("Successfully synced all subcsription permissions."))