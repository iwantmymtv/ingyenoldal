from django.urls import path

from website_builder.websites.views import (
    save_website,
    UserWebsiteList,
    user_website_detail,
    UpladAssets,
    delete_website,
    download_website,
    visit_website,
    redirect_short_website
)

from website_builder.websites.aws_views import (
    host_website_on_s3,
    request_certificate,
    domain_instructions,
    validate_domain,
    check_if_domain_validated,
    host_website_instruction,
)

app_name = "websites"

urlpatterns = [
    path('<uuid:uuid>',view=visit_website,name="visit-website"),
    path("my-websites", view=UserWebsiteList.as_view(), name="website-list"),
    #path('<str:short_id>',view=redirect_short_website,name="visit-website-short"),
    path("my-websites/<uuid:uid>", view=user_website_detail, name="website-detail"),

    path("save-website/",view=save_website,name="save-website"),
    path("upload/assets", view=UpladAssets.as_view(), name="upload-assets"),
    path("delete/<uuid:uid>", view=delete_website, name="delete-website"),
    path("download/<uuid:uid>", view=download_website, name="download-website"),

    path("my-websites/domain/<uuid:uuid>",
        view=domain_instructions, name="website-domain"),
    path('host-website-on-s3/<uuid:uuid>',view=host_website_on_s3,name="host-website"),
    path('request_certificate/<uuid:uuid>',view=request_certificate,name="amc"),
    path('validate_domain/<uuid:uuid>',view=validate_domain,name="validate_domain"),
    path('check_if_domain_validated/<uuid:uuid>',
        view=check_if_domain_validated,
        name="check_validation_status"),
    path('host-website-instruction/<uuid:uuid>',
        view=host_website_instruction,
        name="host-instruction"),

]
