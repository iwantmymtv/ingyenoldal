
from django.contrib import admin
from website_builder.subscriptions.models import (
    Subscription,
    Plan
)

# Register your models here.
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
