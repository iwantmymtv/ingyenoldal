from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubscriptionsConfig(AppConfig):
    name = "website_builder.subscriptions"
    verbose_name = _("Subscriptions")

    def ready(self):
        try:
            import website_builder.subscriptions.signals  # noqa F401
        except ImportError:
            pass
