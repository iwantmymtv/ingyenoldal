from django.forms import ModelForm,CharField
from website_builder.websites.models import Website
from website_builder.builder.widgets import HtmlEditor
from django.utils.translation import gettext_lazy as _

class WebsiteForm(ModelForm):
    slug = CharField(
        required=False,
        min_length=4,
        max_length=30,
        label=_("Subdomain"),
        help_text=_("this will be your subdomain, example: mysite.ngye.in")
        )

    class Meta:
        model = Website
        fields = ['name','slug', 'description','icon']

class WebsiteDomain(ModelForm):
    class Meta:
        model = Website
        fields = ['domain_name']


class WebsiteAdminForm(ModelForm):
    model = Website
    class Meta:
        fields = '__all__'
        widgets = {
            'html_content': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
        }