from django.conf import settings
from django.db import models

# Create your models here.
User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True) #The database may store empty Null and empty values
    init_email = models.EmailField(null=True, blank=True)
    init_email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.stripe_id}"

# 4\. Automatic Customer Creation with Allauth Signals (`customers/signals.py`)