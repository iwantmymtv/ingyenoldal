from django.urls import path

from website_builder.contacts.views import (
    create_contact,
    builder_contact_form
)

app_name = "contacts"

urlpatterns = [
    path("<uuid:uuid>",view=builder_contact_form,name="builder-form"),
    path("new", view=create_contact, name="create-contact"),
]
