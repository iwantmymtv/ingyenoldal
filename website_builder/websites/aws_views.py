import os
import tempfile

from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpRequest, HttpResponse,JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse

from rest_framework.response import Response

from website_builder.websites.models import Website,UploadedAsset,HostedWebsite
from website_builder.builder.models import Template

from website_builder.websites.forms import WebsiteDomain

from website_builder.websites.aws import S3,Acm,CloudFront
from website_builder.websites.utils import (
    get_rendered_html_from_template,
    get_website_if_subscribed,
)

@login_required
def domain_instructions(request:HttpRequest,uuid:str) -> HttpResponse:
    if request.user.has_subscription():
        website = get_object_or_404(Website,uid=uuid,user=request.user)
        #check if hosted
        if website.is_hosted():
            hosted_site = website.get_hosted_site()
            #domain already validated
            if hosted_site.is_validated:
                return redirect(reverse('websites:host-instruction', kwargs={'uuid': website.private_uuid}))
            else:
                return redirect(reverse('websites:amc', kwargs={'uuid': website.private_uuid}))
        else:
            return redirect(reverse('websites:amc', kwargs={'uuid': website.private_uuid}))
    else:
        messages.info(request,_("Only subscribers can connect their domain!"))
        return redirect('subs:pricing-page')

@login_required
def request_certificate(request:HttpRequest,uuid:str) -> HttpResponse:
    website = get_website_if_subscribed(request,uuid)
    if not website:
        return redirect("home")

    hosted_website = website.get_hosted_site()

    if request.method == "POST":
        form = WebsiteDomain(request.POST)
        if form.is_valid():
            domain = form.cleaned_data.get('domain_name')
            acm = Acm()
            response = acm.request_certificate(domain)
            if response:
                arn = response['CertificateArn']
                validation_data = acm.get_domain_validation_records(arn)

                while not validation_data:
                    validation_data = acm.get_domain_validation_records(arn)

                while not 'ResourceRecord' in validation_data[0]:
                    validation_data = acm.get_domain_validation_records(arn)
                name = validation_data[0]["ResourceRecord"]["Name"]
                validation_name = name.split(".")[0]
                validation_value = validation_data[0]["ResourceRecord"]["Value"]

                if hosted_website:
                    hosted_website.delete()

                hosted, created= HostedWebsite.objects.get_or_create(
                    user=request.user,
                    website=website,
                    certificate_arn=arn
                    )
                hosted.validation_host=validation_name
                hosted.validation_value=validation_value[:-1]
                hosted.is_validated = False
                hosted.save()
                print("--------------------")
                print(hosted.validation_host)
                print("---------------------")
                website.domain_name = domain
                website.save()
                return redirect(reverse('websites:validate_domain', kwargs={'uuid': website.private_uuid}))
    else:
        form = WebsiteDomain()
        if hosted_website:
            return redirect(reverse('websites:validate_domain', kwargs={'uuid': website.private_uuid}))

    ctx = {
        "form":form
    }

    return render(request,'websites/request_certificate.html',ctx)

@login_required
def validate_domain(request:HttpRequest,uuid:str) -> HttpResponse:
    website = get_website_if_subscribed(request,uuid)
    hosted_website = website.get_hosted_site() if website else None

    if not website or not hosted_website:
        return redirect("home")

    form = WebsiteDomain(initial={"domain_name":website.domain_name})
    ctx = {
        "hosted":hosted_website,
        "website":website,
        "edit_domain_form":form
    }
    return render(request,"websites/validate_domain.html",ctx)

@login_required
def check_if_domain_validated(request:HttpRequest,uuid:str) -> HttpResponse:
    website = get_website_if_subscribed(request,uuid)
    hosted_website = website.get_hosted_site() if website else None

    if not website or not hosted_website:
        return redirect("home")

    acm = Acm()
    status = acm.get_certificate_status(hosted_website.certificate_arn)
    if not status == 'ISSUED':
        messages.info(request,_(f"Domain validation status is: {status}"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request,_("Domain is validated"))
        hosted_website.is_validated = True
        hosted_website.save()
        return redirect(reverse('websites:host-instruction', kwargs={'uuid': website.private_uuid}))


@login_required
def host_website_instruction(request:HttpRequest,uuid:str) -> HttpResponse:
    website = get_website_if_subscribed(request,uuid)
    hosted_website = website.get_hosted_site() if website else None

    if not website or not hosted_website:
        return redirect("home")

    ctx = {
        'website':website,
        'hosted_website':hosted_website
    }

    return render(request,'websites/host_instruction.html',ctx)


@login_required
def host_website_on_s3(request:HttpRequest,uuid:str) -> HttpResponse:
    website = get_website_if_subscribed(request,uuid)
    hosted_website = website.get_hosted_site() if website else None

    if not website or not hosted_website:
        messages.error(request,_("Something went wrong"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    html = get_rendered_html_from_template(request,website)

    bucket_name = f"{website.user.username}-{website.private_uuid}"
    region = 'eu-central-1'
    s3 = S3(region,bucket_name)

    if not s3.get_bucket():
        s3.create_bucket()
        s3.create_website_config()
        s3.set_bucket_policy()
    url = f"{bucket_name}.s3-website.{region}.amazonaws.com"
    hosted_website.s3_url = url
    hosted_website.save()

    fd, path = tempfile.mkstemp(suffix = '.html')
    # use a context manager to open the file at that path and close it again
    with open(path, 'w') as f:
        f.write(html)
        print(f)

    s3.upload_file(path,'index.html')
        # close the file descriptor
    os.close(fd)

    cloudfront = CloudFront()
    cf = cloudfront.create_distribution(hosted_website)
    print(cf)
    hosted_website.cloudfront_url = cf['Distribution']['DomainName']
    hosted_website.distribution_id = cf['Distribution']['Id']
    hosted_website.save()

    messages.success(request,_("Successfully hosted!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

