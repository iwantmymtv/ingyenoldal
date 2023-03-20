from django.contrib import admin
from website_builder.websites.forms import (
    WebsiteAdminForm,
)
from website_builder.websites.models import (
    Website,
    UploadedAsset,
    HostedWebsite,
    WebsiteExtraPage
)

class PageInline(admin.StackedInline):
    model = WebsiteExtraPage
    extra = 0
# Register your models here.
@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    form = WebsiteAdminForm
    fields = ('user','uid','private_uuid','name','slug','description','icon','domain_name','html_content','css','template','image','modified','created')
    readonly_fields = ('uid','private_uuid','template','modified','created')
    inlines = [PageInline]
    
@admin.register(UploadedAsset)
class UploadedAssetAdmin(admin.ModelAdmin):
    pass

@admin.register(HostedWebsite)
class HostedWebsiteAdmin(admin.ModelAdmin):
    pass
