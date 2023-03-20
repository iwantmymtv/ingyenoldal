from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Contact(models.Model):
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    user = models.ForeignKey(
        User,
        related_name = "contacts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("user")
    )
    subject = models.CharField(
        max_length=128,
        verbose_name=_("subject")
        )
    name = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_("name")
        )
    email = models.EmailField()
    message = models.TextField(verbose_name = _("message"))

    def __str__(self):
        return self.subject
