import stripe
import json

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse,HttpResponse, HttpResponseBadRequest,HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from website_builder.subscriptions.models import Plan
from website_builder.subscriptions.events import (
    payment_success_event,
    payment_failed_event,
    checkout_success_event,
    subscription_created_event,
    subscription_updated_event,
    subscription_ended_event
)


if settings.STRIPE_LIVE_MODE:
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    webhook_secret = settings.STRIPE_LIVE_WEBHOOK
    CURRENT_SITE = f"https://{settings.SITE_DEFAULT_URL}"

else:
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    webhook_secret = settings.STRIPE_TEST_WEBHOOK
    CURRENT_SITE = f"http://localhost:8000"


def pricing_page(request:HttpRequest) -> HttpResponse:
    plans = Plan.objects.filter(is_public=True)
    ctx = {
        "plans":plans,
        "public_key":settings.STRIPE_TEST_PUBLIC_KEY
    }
    return render(request,'subscriptions/pricing_page.html',ctx)

@login_required
def create_checkout_session(request:HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=CURRENT_SITE +'/users/' + request.user.username + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=CURRENT_SITE + '/subscriptions/canceled',
                payment_method_types=['card'],
                customer_email=request.user.email,
                billing_address_collection='required',
                mode='subscription',
                line_items=[{
                    'price': data['priceId'],
                    'quantity': 1
                }],
                metadata={
                    'price_id':data['priceId'],
                }
            )
            ctx = {
                'checkout_session': checkout_session['id']
            }
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': {'message': str(e)}})


@method_decorator(csrf_exempt, name="dispatch")
class ProcessWebhookView(View):
    def post(self, request:HttpRequest) -> HttpResponse:
        if "HTTP_STRIPE_SIGNATURE" not in request.META:
            # Do not even attempt to process/store the event if there is
            # no signature in the headers so we avoid overfilling the db.
            return HttpResponseBadRequest()

        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            print(webhook_secret)
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=webhook_secret
            )
            data = event['data']
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        event_type = event['type']

        #Sent when a customer clicks the Pay or Subscribe button in Checkout,
        # informing you of a new purchase.
        if event_type == 'checkout.session.completed':
            checkout_success_event(data)

        # Sent each billing interval when a payment succeeds.
        elif event_type == 'invoice.paid':
            payment_success_event(data)

        #Sent each billing interval if there is an issue with your customer’s payment method.
        elif event_type == 'invoice.payment_failed':
            payment_failed_event(data)

        #Occurs whenever a customer is signed up for a new plan.
        elif event_type == 'customer.subscription.created':
            subscription_created_event(data)

        #Occurs whenever a subscription changes (e.g., switching from one plan to another,
        # or changing the status from trial to active).
        elif event_type == 'customer.subscription.updated':
            subscription_updated_event(data)

        #Occurs whenever a customer's subscription ends.
        elif event_type == 'customer.subscription.deleted':
            subscription_ended_event(data)
        else:
            print("------------------")
            print(event_type)
            print("------------------")

        return HttpResponse(status=200)

@login_required
def customer_portal(request:HttpRequest) -> JsonResponse:
    if request.method == "POST":
        customer_id = request.user.get_subscription().customer_id
        return_url = CURRENT_SITE
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url)
        return JsonResponse({'url': session.url})
