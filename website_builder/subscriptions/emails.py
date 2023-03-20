from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

def sendEmail(email_path,mail_subject,email_to,**kwargs):
    emailmessage = render_to_string(email_path, kwargs)
    text_content = strip_tags(emailmessage)
    msg = EmailMultiAlternatives(
        mail_subject,
        text_content,
        settings.DEFAULT_EMAIL_SENDER,
        list(email_to)
        )

    msg.attach_alternative(emailmessage, "text/html")
    msg.send()
    print('sended')

    return

def send_subscription_success_email(email,*args,**kwargs):
    sendEmail(
        'subscriptions/emails/created.html',
        _('Subscription successful'),
        email,
    )
    return

def send_subscription_failed_email(email,*args,**kwargs):
    sendEmail(
        'subscriptions/emails/sub_failed.html',
        _('Subscription failed'),
        email,
        kwargs
    )
    return

def send_invoice_paid_success_email(email,*args,**kwargs):
    sendEmail(
        'subscriptions/emails/payment_success.html',
        _('Payment successful'),
        email,
        kwargs
    )
    return

def send_invoice_paid_failed_email(email,*args,**kwargs):
    sendEmail(
        'subscriptions/emails/payment_failed.html',
        _('Payment failed'),
        email,
        kwargs
    )
    return

def send_cancel_subscription_email(email,*args,**kwargs):
    sendEmail(
        'subscriptions/emails/sub_canceled.html',
        _('Subscription canceled'),
        email,
        end_date=kwargs['end_date']
    )
    return
