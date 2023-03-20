from django.contrib import admin
from website_builder.contacts.models import (
    Contact
)

# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass
