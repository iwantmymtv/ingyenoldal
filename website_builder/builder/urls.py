from django.urls import path

from website_builder.builder.views import (
    TemplateList,
    TemplateDetail,
    builder_view,
    template_preview,
    template_preview_extra_pages,
    download_template
)
from website_builder.builder.api import (
    GetTemplate,
    GetUserUploadedAssets
)

app_name = "builder"

urlpatterns = [
    path("", view=TemplateList.as_view(), name="template-list"),
    path("<slug:slug>", view=TemplateDetail.as_view(), name="template-detail"),
    path("preview/<slug:slug>", view=template_preview, name="template-preview"),
    path("preview/<slug:slug>/<str:page_slug>", view=template_preview_extra_pages, name="template-preview-extra"),

    path("builder/<uuid:id>", view=builder_view, name="builder"),
    path("builder/<int:id>", view=builder_view, name="builder"),
    path("download/<int:id>", view=download_template, name="download"),
    #api urls
    path("api/v1/template/<uuid:id>",view=GetTemplate.as_view(),name="get-template-api"),
    path("api/v1/template/<int:id>",view=GetTemplate.as_view(),name="get-template-api"),
    path("api/v1/user-assets",view=GetUserUploadedAssets.as_view(),name="get-user-assets"),

]
