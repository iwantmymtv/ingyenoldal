from django.contrib.auth.models import AbstractUser
from django.db.models import CharField,ForeignKey,SET_NULL
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for website-builder."""

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def get_absolute_url(self) -> str:
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def has_subscription(self) -> bool:
        try:
            self.subscription
            return True
        except:
            return False

    def get_subscription(self):
        if self.has_subscription():
            return self.subscription
        return None

    def get_subscription_end_date(self):
        if self.get_subscription():
            return self.get_subscription().end_date
        return None
