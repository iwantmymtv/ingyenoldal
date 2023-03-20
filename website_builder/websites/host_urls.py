from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from website_builder.websites.views import (
    visit_website_with_subdomain,
    visit_website_extra
)

app_name = "websites"

urlpatterns = [
    path("", view=visit_website_with_subdomain, name="view-website"),
    path("<slug:slug>", view=visit_website_extra, name="view-website-extra"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls))
        ]
