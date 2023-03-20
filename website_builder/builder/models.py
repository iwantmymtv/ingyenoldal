import uuid
from bs4 import BeautifulSoup
import htmlmin

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill,ResizeToFit
from website_builder.builder.utils import create_links_for_template

User = get_user_model()

# Create your models here.
class TemplateCategory(models.Model):
    class Meta:
        verbose_name = _("Template Category")
        verbose_name_plural = _("Template Categories")

    name = models.CharField(max_length=128,verbose_name=_("name"))
    description = models.TextField(max_length=500,verbose_name=_("description"))
    image = models.ImageField(blank=True,verbose_name=_("image"))

    def __str__(self):
        return self.name

class Font(models.Model):
    class Meta:
        verbose_name = _("Style")
        verbose_name_plural = _("Styles")

    name = models.CharField(max_length=50,verbose_name=_("name"))
    url_path = models.URLField(blank=True,verbose_name=_("url path"))

    def __str__(self):
        return self.name


class Style(models.Model):
    class Meta:
        verbose_name = _("Style")
        verbose_name_plural = _("Styles")

    name = models.CharField(max_length=50,verbose_name=_("name"))
    style = models.TextField(blank=True,verbose_name=_("style"))
    url_path = models.URLField(blank=True,verbose_name=_("url path"))

    def __str__(self):
        return self.name

class Script(models.Model):
    class Meta:
        verbose_name = _("Script")
        verbose_name_plural = _("Scripts")

    name = models.CharField(max_length=50,verbose_name=_("name"))
    script = models.TextField(blank=True,verbose_name=_("script"))
    url_path = models.URLField(blank=True,verbose_name=_("url path"))
    is_defered = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Template(models.Model):
    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        ordering = ('-timestamp',)
    name = models.CharField(max_length=128,verbose_name=_("name"))
    slug = models.SlugField(default="")
    description = models.TextField(max_length=500,verbose_name=_("description"))
    category = models.ForeignKey('TemplateCategory',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("category")
        )
    html_content = models.TextField(verbose_name=_("html content"))
    image = models.ImageField(verbose_name=_("image"))
    image_thumbnail = ImageSpecField(source='image',
                                           processors=[ResizeToFill(576,324)],
                                           options={'quality': 80})
    is_public = models.BooleanField(default=False,verbose_name=_("is public"))
    is_premium = models.BooleanField(default=False,verbose_name=_("is premium"))
    
    styles = models.ManyToManyField('Style',blank=True,verbose_name=_("styles"))
    scripts = models.ManyToManyField('Script',blank=True,verbose_name=_("scripts"))
    fonts = models.ManyToManyField('Fonts',blank=True,verbose_name=_("fonts"))

    timestamp = models.DateTimeField(default=timezone.now)
    is_editable = models.BooleanField(default=True,verbose_name=_("is editable"))

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.html_content = create_links_for_template(self.html_content,self.slug)
        super().save(*args,**kwargs)

    def get_absolute_url(self) -> str:
        return reverse('builder:template-detail', kwargs={'slug': self.slug})

    def get_builder_url(self) -> str:
        return reverse('builder:builder', kwargs={'id': self.id})

    def get_download_url(self) -> str:
        return reverse('builder:download', kwargs={'id': self.id})

    def get_preview_url(self) -> str:
        return reverse('builder:template-preview', kwargs={'slug': self.slug})

class Page(models.Model):
    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        abstract = True

    page_id = models.CharField(max_length=50)
    name = models.CharField(max_length=128,verbose_name=_("name"),default='index')
    html_content = models.TextField(verbose_name=_("html content"),default='')
    css = models.TextField(blank=True)

    def __str__(self):
        return self.name

class TemplateExtraPage(Page):
    template = models.ForeignKey('Template',related_name="pages",on_delete=models.CASCADE)
      
    def save(self,*args,**kwargs):
        self.html_content = create_links_for_template(self.html_content,self.template.slug)
        super().save(*args,**kwargs)

class BlockCategory(models.Model):
    class Meta:
        verbose_name = _("Block category")
        verbose_name_plural = _("Block categories")

    name = models.CharField(max_length=50,verbose_name=_("name"))
    def __str__(self):
        return self.name

class AttributeType(models.Model):
    class Meta:
        verbose_name = _("Attribute type")
        verbose_name_plural = _("Attribute types")

    name = models.CharField(max_length=50,verbose_name=_("name"))
    def __str__(self):
        return self.name

class BlockAttributes(models.Model):
    class Meta:
        verbose_name = _("BlockAttribute")
        verbose_name_plural = _("BlockAttributes")

    type = models.ForeignKey('AttributeType', on_delete=models.CASCADE,verbose_name=_("type"))
    value = models.CharField(max_length=128,verbose_name=_("value"))
    def __str__(self):
        return f"{self.type.name} - {self.value}"

class Block(models.Model):
    class Meta:
        verbose_name = _("Block")
        verbose_name_plural = _("Blocks")

    uid = models.UUIDField(
        primary_key = False,
        default = uuid.uuid4,
        editable = False
    )
    name = models.CharField(max_length=128,verbose_name=_("name"))
    style = models.ManyToManyField('Style',
        related_name="blocks",
        blank=True,
        )
    script = models.ManyToManyField('Script',
        related_name="blocks",
        blank=True,
        )
    category = models.ForeignKey('BlockCategory',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("category")
        )
    image = models.ImageField(blank=True,verbose_name=_("image"))
    image_thumbnail = ImageSpecField(source='image',
                                           processors=[ResizeToFit(250)],
                                           options={'quality': 80})
    html_content = models.TextField(verbose_name=_("html content"))
    attributes = models.ManyToManyField("BlockAttributes",
        blank=True,
        verbose_name=_("attributes")
        )
    info_content = models.TextField(blank=True,null=True)
    
    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        self.html_content=htmlmin.minify(
            self.html_content,
            remove_comments=True,
            remove_optional_attribute_quotes=False,
            remove_empty_space=True)
        super().save()

