from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebsitesConfig(AppConfig):
    name = "website_builder.websites"
    verbose_name = _("Websites")

    def ready(self):
        try:
            import website_builder.websites.signals  # noqa F401
        except ImportError:
            pass
