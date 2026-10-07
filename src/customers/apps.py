# Defines the configuration for your customers and load its signal handlers when Django starts\

# Imports Django's base application-configuration class
from django.apps import AppConfig

# Configuration class for the customers app
class CustomersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  #Sets the default type for automatically generated primary-key fields
    name = 'customers'  #Tells Django the app's Python package name

    def ready(self):
        # Loads customers/signals.py, importing that file registers the signal receivers, such as the handler for email_confirmed
        import customers.signals