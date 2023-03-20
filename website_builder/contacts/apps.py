from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContactsConfig(AppConfig):
    name = "website_builder.contacts"
    verbose_name = _("Contacts")

    def ready(self):
        try:
            import website_builder.contacts.signals  # noqa F401
        except ImportError:
            pass
