import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django_hosts.resolvers import reverse as host_reverse
from django.core.validators import RegexValidator
from django.core.cache import cache

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill,ResizeToFit

from website_builder.builder.models import Template,Page
User = get_user_model()

BASE_ALPH = tuple("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
BASE_DICT = dict((c, v) for v, c in enumerate(BASE_ALPH))
BASE_LEN = len(BASE_ALPH)

def base_decode(string):
    num = 0
    for char in string:
        num = num * BASE_LEN + BASE_DICT[char]
    return num

def base_encode(num):
    if not num:
        return BASE_ALPH[0]

    encoding = ""
    while num:
        num, rem = divmod(num, BASE_LEN)
        encoding = BASE_ALPH[rem] + encoding
    return encoding

def encode_uuid(uuid_param):
    id = uuid.UUID(uuid_param)
    uuid62 = base_encode(id.int)
    return uuid62

def decode_uuid(encoded_uuid):
    id = uuid.UUID(int=base_decode(encoded_uuid))
    return str(id)
    
# Create your models here.
class Website(models.Model):
    DOMAIN_NAME_REGEX = RegexValidator(
        r"^(?!http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$",
        _('Domain is not valid (do not use http(s)://)'))

    class Meta:
        verbose_name = _("Website")
        verbose_name_plural = _("Websites")
        ordering = ("-modified",)

    user = models.ForeignKey(
        User,
        related_name = "websites",
        on_delete=models.CASCADE,
        verbose_name=_("user")
    )
    uid = models.UUIDField(
        primary_key = False,
        default = uuid.uuid4,
        editable = False
    )
    private_uuid = models.UUIDField(
        primary_key = False,
        default = uuid.uuid4,
        editable = False
    )
    name = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_("name")
        )
    slug = models.SlugField(
        verbose_name=_("Subdomain"),
        unique=True,
        null=True,
        blank=True,
        help_text=_("this will be your subdomain, example: mysite.ngye.in"))
    description = models.TextField(
        blank=True,
        verbose_name=_("description")
        )
    icon = models.ImageField(blank=True)
    icon_small = ImageSpecField(source='icon',
                                processors=[ResizeToFit(32)],
                                format='PNG',
                                options={'quality': 30})
    domain_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        validators=[DOMAIN_NAME_REGEX],
        verbose_name=_("domain name")
        )
    html_content = models.TextField(verbose_name=_("HTML content"))
    css = models.TextField()
    template = models.ForeignKey(Template,
        blank=True,
        related_name="created_websites",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Template"))
    image = models.ImageField(blank=True,verbose_name=_("image"))
    image_thumbnail = ImageSpecField(source='image',
                                           processors=[ResizeToFit(500)],
                                           options={'quality': 80})
    modified = models.DateTimeField(default=timezone.now,verbose_name=_("modified at"))
    created = models.DateTimeField(default=timezone.now,verbose_name=_("created at"))

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('websites:website-detail', kwargs={'uid': self.uid})

    def get_builder_url(self) -> str:
        return reverse('builder:builder', kwargs={'id': self.uid})

    def get_delete_url(self) -> str:
        return reverse('websites:delete-website', kwargs={'uid': self.uid})

    def get_download_url(self) -> str:
        return reverse('websites:download-website', kwargs={'uid': self.uid})

    def get_visit_url(self) -> str:
        return reverse('websites:visit-website', kwargs={'uuid': self.uid})

    def get_live_url(self) -> str:
        subdomain = self.private_uuid
        if self.slug:
            subdomain = self.slug
        
        if settings.DEBUG:
            return f"http://{subdomain}.localhost:8000"
        else:
            return f"https://{subdomain}.ngye.in"

    def get_hosted_site(self):
        if self.hosted_sites.all().count() > 0:
            return self.hosted_sites.first()
        return None

    def get_short_url(self) -> str:
        return f"http://ngye.in/{encode_uuid(str(self.uid))}"

    def is_hosted(self) -> bool:
        if self.hosted_sites.all().count() > 0:
            return True
        return False

    def save(self, *args, **kwargs) -> None:
        caches_list = [
            f"website-{self.private_uuid}",
            f"website-{self.uid}",
            f"website-{self.slug}",
            f"website-extra-{self.slug}"
        ]
        cache.delete_many(caches_list)

        self.modified = timezone.now()
        super().save()

class WebsiteExtraPage(Page):
    website = models.ForeignKey('Website',related_name="pages",on_delete=models.CASCADE)


class HostedWebsite(models.Model):
    user = models.ForeignKey(
        User,
        related_name = "hosted_sites",
        on_delete=models.CASCADE,
        verbose_name=_("user")
    )
    website = models.ForeignKey('Website',related_name="hosted_sites", on_delete=models.CASCADE)
    s3_url = models.URLField(blank=True)
    cloudfront_url = models.URLField(blank=True)
    distribution_id = models.CharField(max_length=50,blank=True)
    certificate_arn = models.CharField(max_length=255,blank=True)
    validation_host = models.CharField(max_length=50,blank=True)
    validation_value = models.CharField(max_length=255,blank=True)
    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.website)

    def get_bucket_name(self):
        if self.s3_url:
            return self.s3_url.replace("http://","").split(".")[0]
        return None

    def get_region(self):
        if self.s3_url:
            return self.s3_url.replace("http://","").split(".")[2]
        return None

class UploadedAsset(models.Model):
    user = models.ForeignKey(
        User,
        related_name = "assests",
        on_delete=models.CASCADE,
        verbose_name=_("user")
    )
    name = models.CharField(max_length=255, blank=True,verbose_name=_("name"))
    asset = models.FileField(upload_to='assests/',verbose_name=_("asset"))
    asset_thumbnail = ImageSpecField(source='asset',
                                           processors=[ResizeToFit(500)],
                                           options={'quality': 60})
    uploaded_at = models.DateTimeField(default=timezone.now,verbose_name=_("upload time"))

    def __str__(self):
        return self.name
