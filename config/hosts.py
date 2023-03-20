from django_hosts import patterns, host
from django.conf import settings

host_patterns = patterns(
    '',
    host(r"www",settings.ROOT_URLCONF, name="default-website"),
    #uuid regex
    host(r"[A-Za-z0-9-]{4,}",
     "website_builder.websites.host_urls",
     name="wildcard"),

)

