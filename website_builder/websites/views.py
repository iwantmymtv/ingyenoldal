
import json,io,zipfile
from ratelimit.decorators import ratelimit

from django.conf import settings
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpRequest, HttpResponse,JsonResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files import uploadedfile
from django.views.generic import ListView
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.response import Response

from website_builder.websites.models import (
    Website,
    UploadedAsset,
    WebsiteExtraPage,
    decode_uuid
)
from website_builder.builder.models import Template
from website_builder.builder.utils import is_valid_uuid

from website_builder.websites.forms import WebsiteForm
from website_builder.websites.serializers import SaveWebsiteSerializer
from website_builder.websites.utils import (
    get_rendered_html_from_template,
    upload_html_to_s3,
    get_identifier_from_subdomain,
    remove_template_slug_from_links,
    compile_website,
    compile_extra_page
)


class UpladAssets(APIView):
    def post(self,request:HttpRequest) -> Response:
        img_urls = []
        for i in request.data.getlist("assets[]"):
            print(request.data.getlist("assets[]"))
            if isinstance(i,uploadedfile.TemporaryUploadedFile) or isinstance(i,uploadedfile.InMemoryUploadedFile):
                u_file = UploadedAsset.objects.create(
                    name=i.name,
                    asset=i,
                    user=request.user
                    )
                img_urls.append(u_file.asset_thumbnail.url)
        return Response({"data": img_urls})

class UserWebsiteList(ListView,LoginRequiredMixin):
    paginate_by = 6
    context_object_name = 'website_list'
    template_name = "websites/user_website_list.html"

    def get_queryset(self):
        user = self.request.user
        return user.websites.all()

@login_required
def user_website_detail(request: HttpRequest,uid:str) -> HttpResponse:
    website = get_object_or_404(Website,uid=uid,user=request.user)
    form = WebsiteForm(instance=website)

    if request.method == "POST":
        form = WebsiteForm(request.POST,request.FILES,instance=website)

        if form.is_valid():
            f = form.cleaned_data

            for i in f:
                if not getattr(website,i) == f.get(i):
                    if f.get(i):
                        setattr(website,i,f.get(i))

            hosted_site = website.get_hosted_site()
            if hosted_site:
                upload_html_to_s3(
                    request,
                    website,
                    hosted_site.get_bucket_name(),
                    hosted_site.get_region())

            website.save()

            messages.success(request,_("Successfully updated!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    ctx = {
        "website":website,
        "form":form
    }
    return render(request,"websites/user_website_detail.html",ctx)

@login_required
def save_website(request:HttpRequest) -> JsonResponse:
    user = request.user
    if request.method == "POST":
        data = json.loads(request.body)
        serializer = SaveWebsiteSerializer(data=data)

        if serializer.is_valid():
            #chek how many pages they have
            if user.has_subscription():
                if len(data["extra_pages"]) > user.get_subscription().plan.max_page_per_site:
                    return JsonResponse({"error":"Too many pages"})
            else:
                if len(data["extra_pages"]) > 5:
                    return JsonResponse({"error":"Too many pages"})
            
            #xhwxk if website already exists
            if "website_id" in data:
                website = get_object_or_404(Website,uid=data["website_id"],user=request.user)
                website.html_content = data["html_content"]
                website.css = data["css"]
            else:
                website = Website.objects.create(
                    user=request.user,
                    html_content=data["html_content"],
                    css=data["css"],
                    template=Template.objects.get(id=data["template_id"])
                )
                website.html_content = remove_template_slug_from_links(
                    website.html_content,
                    website.template.slug
                )

            #create name 
            if not website.name:
                wbc = Website.objects.filter(user=request.user).count()
                website.name = f"{website.user.username}_website({wbc})"

            #if deleted all pages but the index
            if website.pages.all().count() > 0 and len(data["extra_pages"]) == 0:
                website.pages.all().delete()
            
            #save extra pages
            if len(data["extra_pages"]) > 0:
                website.pages.all().delete()
                extra_page_list = []
                for i in data["extra_pages"]:
                    ep= WebsiteExtraPage(
                        website=website,
                        page_id=i["page_id"],
                        name=i["name"],
                        html_content=i["html_content"],
                        css=i["css"]
                    )
                    ep.html_content = remove_template_slug_from_links(
                        ep.html_content,
                        website.template.slug
                    )
                    extra_page_list.append(ep)
                WebsiteExtraPage.objects.bulk_create(extra_page_list)
            #if "image" in data:
            #   website.image = base64_file(data["image"],name=website.uid)
            website.save()
            return JsonResponse({"uid":website.uid})
        return JsonResponse({"error":"Wrong data"})

def visit_website_with_subdomain(request:HttpRequest) -> HttpResponse:
    uuid = get_identifier_from_subdomain(request)
    return visit_website(request,uuid,False)



@xframe_options_exempt
def visit_website(request:HttpRequest,uuid:str,public:bool=True)-> HttpResponse:
    context = cache.get(f"website-{uuid}")
    if not context:
        if is_valid_uuid(uuid):
            if public:
                website = get_object_or_404(Website,uid=uuid)
            else:
                website = get_object_or_404(Website,private_uuid=uuid)
        else:
            website = get_object_or_404(Website,slug=uuid)

        ctx = compile_website(website)
        cache.set(f"website-{uuid}",ctx,int(settings.WEBSITE_CACHE_TIME))
        context = cache.get(f"website-{uuid}")

    return render(request,"websites/index.html",context)

@xframe_options_exempt
def visit_website_extra(request:HttpRequest,slug:str) -> HttpResponse:
    uuid = get_identifier_from_subdomain(request)
    #check if cached
    context = cache.get(f"website-extra-{slug}")
    if not context:
        if is_valid_uuid(uuid):
            website = get_object_or_404(Website,private_uuid=uuid)
        else:
            website = get_object_or_404(Website,slug=uuid)

        page = get_object_or_404(WebsiteExtraPage,website=website,page_id=slug)
        ctx = compile_website(website)
        ctx["page"] = compile_extra_page(page)
        cache.set(f"website-extra-{slug}",ctx,int(settings.WEBSITE_CACHE_TIME))
        context = cache.get(f"website-extra-{slug}")

    return render(request,"websites/index.html",context)

@login_required
def delete_website(request:HttpRequest,uid:str)-> HttpResponseRedirect:
    website = get_object_or_404(Website,uid=uid,user=request.user)
    website.delete()
    return HttpResponseRedirect(reverse("websites:website-list"))


@ratelimit(key='ip', rate='1/h')
@login_required
def download_website(request:HttpRequest,uid:str)-> HttpResponseRedirect:
    was_limited = getattr(request, 'limited', False)

    if was_limited:
        messages.info(request,_("Download limit is: 1 website / hour"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    website = get_object_or_404(
            Website,
            uid=uid,
            user=request.user
        )

    rendered  = get_rendered_html_from_template(request,website)

    main_dir_name = website.name
    html = rendered["html"]
    images = rendered["images"]

    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')

    #write index file
    zip_file.writestr(f'{main_dir_name}/index.html', html)
    
    #get imageas from index
    if images:
        for i in images:
            zip_file.writestr(f"{main_dir_name}/images/{i['name']}.{i['format']}", i["image"])

    if website.pages.all().count() > 0:
        for p in website.pages.all():
            page_rendered  = get_rendered_html_from_template(request,website,p)
            p_html = page_rendered["html"]
            p_images = page_rendered["images"]

            if p_images:
                for i in p_images:
                    zip_file.writestr(f"{main_dir_name}/images/{i['name']}.{i['format']}", i["image"])
            zip_file.writestr(f'{main_dir_name}/{p.page_id}.html', p_html)

    zip_file.close()
    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = f'attachment; filename={website.name}.zip'

    return response

def redirect_short_website(request:HttpRequest,short_id:str) -> HttpResponseRedirect:
    uuid = decode_uuid(short_id)
    return redirect(reverse('websites:visit-website', kwargs={'uuid': uuid}))