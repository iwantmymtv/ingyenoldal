from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Plan(models.Model):
    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")

    name = models.CharField(max_length=50,verbose_name=_("name"))
    description = models.TextField(verbose_name=_("description"),blank=True)
    stripe_price_id = models.CharField(max_length=50)
    price = models.IntegerField(verbose_name=_("price"))
    enabled_websites = models.PositiveIntegerField(default=2)
    is_public = models.BooleanField(default=False)
    can_download = models.BooleanField(default=False)
    can_host_website_on_aws = models.BooleanField(default=False)
    can_use_premium = models.BooleanField(default=True)
    form_submissions = models.IntegerField(default=300)
    asset_size = models.BigIntegerField(default=1024000000)
    max_page_per_site = models.IntegerField(default=5)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    ACTIVE = 'A'
    PAST_DUE = 'PD'
    CANCELED = 'C'
    INCOMPLETE = 'IN'
    INCLOMPLETE_EXPIRED = 'IE'
    PAYMENT_FAILED = 'PF'
    ENDED = 'E'

    STATUSES = [
        (ACTIVE, _('Active')),
        (PAST_DUE, _('Past due')),
        (CANCELED, _('Canceled')),
        (INCOMPLETE, _('Incomplete')),
        (INCLOMPLETE_EXPIRED, _('Incomplete expired')),
        (PAYMENT_FAILED, _('Payment failed')),
        (ENDED, _('Ended')),
    ]
    user = models.OneToOneField(
        User,
        related_name="subscription",
        on_delete=models.CASCADE,
        verbose_name=_("user"))
    status = models.CharField(
        max_length=2,
        choices=STATUSES,
        default=INCOMPLETE,
        verbose_name=_("status"))
    end_date = models.DateTimeField(
        verbose_name=_("end date"),
        default=timezone.now)
    plan = models.ForeignKey(
        'Plan',
        on_delete=models.PROTECT,
        verbose_name=_("plan"),
        related_name="subscriptions")
    customer_id = models.CharField(max_length=50)
    subscription_id = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username}:{self.plan.name} - {self.status}"
