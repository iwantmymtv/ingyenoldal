from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BuilderConfig(AppConfig):
    name = "website_builder.builder"
    verbose_name = _("Builder")

    def ready(self):
        try:
            import website_builder.builder.signals  # noqa F401
        except ImportError:
            pass
