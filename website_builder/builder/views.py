import json
from uuid import UUID
from ratelimit.decorators import ratelimit

from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpRequest, HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView,ListView
from django.views.decorators.cache import cache_page

from django.db.models import Q
from django.contrib import messages
from django.utils import timezone

from website_builder.builder.models import (
    Template,
    Block,
    TemplateCategory,
    Style,
    TemplateExtraPage
)
from website_builder.websites.models import Website,UploadedAsset
from website_builder.builder.utils import is_valid_uuid
from website_builder.websites.utils import (
    get_rendered_html_from_template
)


class TemplateList(ListView):
    paginate_by = 6
    queryset = Template.objects.filter(is_public=True)
    context_object_name = 'template_list'
    template_name = "builder/template_list.html"

    current_category = 0
    current_css = 0

    filters = Q(is_public=True)

    def check_if_empty(self,param):
        if param == '':
            return True
        return False

    def check_if_digit(self,param):
        if not self.check_if_empty(param):
            if param.isdigit():
               return True
        return False

    def get_queryset(self):
        category = self.request.GET.get('category','')
        css = self.request.GET.get('css','')

        if self.check_if_digit(category):
            self.filters &= Q(category=category)
            self.current_category = int(category)

        if self.check_if_digit(css):
            self.filters &= Q(styles=css)
            self.current_css = int(css)

        try:
            templates = Template.objects.filter(self.filters)
        except:
            templates = Template.objects.filter(is_public=True)

        return templates

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = TemplateCategory.objects.all()
        styles = Style.objects.filter(style__exact='')


        current_dict = {
            'category': {
                'name':_("Categories"),
                'obj': categories,
                'current_id':self.current_category,
                'extra_params':{
                    'css': self.current_css,
                }
            },
            'css': {
                'name':"CSS",
                'obj': styles,
                'current_id':self.current_css,
                'extra_params':{
                    'category': self.current_category,
                }
            }
        }

        context['current_dict'] = current_dict

        return context

class TemplateDetail(DetailView):
    queryset = Template.objects.all()
    context_object_name = 'template'
    template_name = "builder/template_detail.html"
    slug_url_kwarg = 'slug'


@login_required
def builder_view(request: HttpRequest,id) -> HttpResponse:
    user = request.user
    website = None
    max_page = 5

    if is_valid_uuid(id):
        website = get_object_or_404(Website,uid=id,user=user)
        template = website.template
    else:
        template = get_object_or_404(Template,id=id,is_editable=True)

        if user.has_subscription() and user.get_subscription_end_date() > timezone.now():
            user_sub = user.get_subscription()
            if user.websites.all().count() >= user_sub.plan.enabled_websites:
                messages.info(request,_("You have reached the maximum websites you can have in this plan!"))
                return redirect("subs:pricing-page")
        else:
            if user.websites.all().count() >= 1:
                messages.info(request,_("Only active subscribers can have more than 1 websites!"))
                return redirect("subs:pricing-page")
            if template.is_premium:
                messages.info(request,_("Only subscribers can use premium templates!"))
                return redirect("subs:pricing-page")

    if user.has_subscription():
        max_page = user.get_subscription().plan.max_page_per_site

    ctx = {
        "template":template,
        "max_page":max_page
    }
    if website:
        ctx["website"] = website

    return render(request,"builder/template_builder.html",ctx)

@cache_page(60*60*24)
def template_preview(request:HttpRequest,slug:str)-> HttpResponse:
    template = get_object_or_404(Template,slug=slug)
    ctx = {
        "template":template
    }
    return render(request,"builder/template_preview.html",ctx)

@cache_page(60*60*24)
def template_preview_extra_pages(request:HttpRequest,slug:str,page_slug:str)-> HttpResponse:
    template = get_object_or_404(Template,slug=slug)
    page = get_object_or_404(TemplateExtraPage,template=template,page_id=page_slug)
    ctx = {
        "template":template,
        "page":page
    }
    return render(request,"builder/template_preview.html",ctx)

@ratelimit(key='ip', rate='1/h')
@login_required
def download_template(request:HttpRequest,id:str)-> HttpResponseRedirect:
    was_limited = getattr(request, 'limited', False)

    if was_limited:
        messages.info(request,_("Download limit is: 1 template / hour"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    template = get_object_or_404(Template,id=id)
    html  = get_rendered_html_from_template(request,template)
    user = request.user
    sub = user.get_subscription()

    if not sub or not sub.plan.can_download or not sub.end_date > timezone.now():
        messages.info(request,_("You cannot download with this plan"))
        return redirect("subs:pricing-page")

    response = HttpResponse(html, content_type='application/html')
    response['Content-Disposition'] = f'attachment; filename={template.name}.html'
    return response
    
   


