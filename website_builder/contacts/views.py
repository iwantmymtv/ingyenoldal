from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse,HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives,send_mail
from django.utils.html import strip_tags

from website_builder.contacts.forms import ContactForm
from website_builder.contacts.models import Contact
from website_builder.websites.models import Website
from website_builder.subscriptions.emails import sendEmail

def create_contact(request:HttpRequest)-> HttpResponse:
    user = request.user
    if user.is_authenticated:
        form = ContactForm(initial={"email":user.email})
    else:
        form = ContactForm()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            print("hello")
            if user.is_authenticated:
                contact = form.save()
                contact.user = user
                contact.save()
            else:
                form.save()

            messages.success(request,_("Email send successfully!"))
            return redirect("home")
        else:
            messages.error(request,_("Something went wrong! Try again..."))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    ctx = {
        "form":form
    }

    return render(request,"contacts/create_contact.html",ctx)


@csrf_exempt
def builder_contact_form(request,uuid):
    host = request.META['HTTP_HOST']
    redirect_url = host
    print("------------hello")
    print("------------hello")
    if 'HTTP_REFERER' in request.META:
        referrer = request.META['HTTP_REFERER']
        redirect_url = referrer

    print("------------meta")
    print(host)
    print(request.headers)
    print(settings.DEFAULT_EMAIL_SENDER)
    print(redirect_url)
    print("------------meta")
    if not host == settings.SITE_DEFAULT_URL or not host == "ngye.in":
        return HttpResponseRedirect(redirect_url)

    if request.method == "POST":
        try:
            website = Website.objects.get(private_uuid=uuid)
            inputs = request.POST.items()
            inputs_dict = {}
            email_list = []
            email_list.append(website.user.email)

            for k,v in inputs:
                inputs_dict[k] = str(v)
                print(k,v)
            print(inputs_dict)
            emailmessage = render_to_string('contacts/emails/builder_forms.html', {"inputs":inputs_dict,"website":website.name})
            text_content = strip_tags(emailmessage)

            msg = EmailMultiAlternatives(
                'New Email',
                text_content,
                settings.DEFAULT_EMAIL_SENDER,
                email_list
                )
            msg.attach_alternative(emailmessage, "text/html")
            msg.send()

        except:
            return HttpResponseRedirect(redirect_url)

    else:
        return HttpResponseRedirect(redirect_url)
    return HttpResponseRedirect(redirect_url)
