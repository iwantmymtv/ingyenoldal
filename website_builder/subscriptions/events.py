import stripe
import datetime
from django.utils.timezone import make_aware
from django.conf import settings
from website_builder.subscriptions.models import Plan,Subscription
from website_builder.subscriptions.emails import (
    send_subscription_success_email,
    send_subscription_failed_email,
    send_invoice_paid_success_email,
    send_invoice_paid_failed_email,
    send_cancel_subscription_email
)

from django.contrib.auth import get_user_model
User = get_user_model()

if settings.STRIPE_LIVE_MODE:
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    webhook_secret = settings.STRIPE_LIVE_WEBHOOK
else:
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    webhook_secret = settings.STRIPE_TEST_WEBHOOK


def update_subscription_object(sub:Subscription,stripe_data:dict,status=None) -> None:
    if status:
        sub.status = status
    sub.end_date = parse_end_date(stripe_data['current_period_end'])
    sub.save()
    return

def parse_end_date(date_unix:int) -> datetime:
    end_date = make_aware(
        datetime.datetime.fromtimestamp(
            float(date_unix)
            )
        )
    return end_date

def payment_success_event(data:dict) -> None:
    print('invoioce paid')
    obj = data['object']
    #TODO:send emial
    try:
        sub = Subscription.objects.get(subscription_id=obj['id'])
    except:
        return

    update_subscription_object(sub,obj,'A')
    send_invoice_paid_success_email(sub.user.email)
    return

def payment_failed_event(data:dict) -> None:
    obj = data['object']
    #email here
    try:
        sub = Subscription.objects.get(subscription_id=obj['id'])
    except:
        return

    update_subscription_object(sub,obj,'PF')
    send_invoice_paid_failed_email(sub.user.email)
    return

def checkout_success_event(data:dict) -> None:
    print("checkout",data['object'])
    obj = data['object']
    stripe_sub = stripe.Subscription.retrieve(obj['subscription'])
    end_date = parse_end_date(stripe_sub['current_period_end'])
    user = User.objects.get(email=obj['customer_email'])
    plan = Plan.objects.get(stripe_price_id=obj["metadata"]["price_id"])
    sub = Subscription.objects.create(
        user=user,
        status='A',
        customer_id=obj['customer'],
        plan=plan,
        end_date=end_date,
        subscription_id=obj['subscription']
    )
    #send_subscription_success_email(user.email)
    return

def subscription_created_event(data:dict) -> None:
    #TODO: send email
    obj = data['object']
    print('sub created')
    customer = stripe.Customer.retrieve(obj['customer'])
    send_subscription_success_email(customer['email'])
    return

def subscription_updated_event(data:dict) -> None:
    print("updates",data['object'])
    obj = data['object']
    try:
        sub = Subscription.objects.get(subscription_id=obj['id'])
    except:
        return
    stripe_plan = obj['items']['data'][0]['plan']

    #if cancels in dashboard
    if obj['canceled_at']:
        sub.status = 'C'
        send_cancel_subscription_email(
            sub.user.email,
            end_date=parse_end_date(obj['current_period_end'])
            )
    #if renews in dashboard
    else:
        sub.status = 'A'

    #if changes plan
    if not int(stripe_plan['amount'])/100 == sub.plan.price:
        sub.plan = Plan.objects.get(stripe_price_id=stripe_plan['id'])

    #change end date just in case
    update_subscription_object(sub,obj)
    return

def subscription_ended_event(data:dict) -> None:
    print("endedS")
    obj = data['object']
    try:
        sub = Subscription.objects.get(subscription_id=obj['id'])
    except:
        return

    if not obj['request']:
        update_subscription_object(sub,obj,'E')

    return
