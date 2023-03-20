from django.urls import path

from website_builder.subscriptions.views import (
    pricing_page,
    create_checkout_session,
    ProcessWebhookView,
    customer_portal
)

app_name = "subs"

urlpatterns = [
    path("", view=pricing_page, name="pricing-page"),
    path("create-checkout-session", view=create_checkout_session, name="create-checkout-session"),
    path("webhooks", view=ProcessWebhookView.as_view(), name="stripe-webhooks"),
    path('customer-portal',view=customer_portal,name="customer-portal")
]
