from django.urls import path
from .views import checkout_redirect_view, checkout_finalize_view

urlpatterns = [
    path("sub/<int:price_id>/", checkout_redirect_view, name="checkout_start"),
    path("success/", checkout_finalize_view, name="checkout_success"),
]