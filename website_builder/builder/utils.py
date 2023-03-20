import uuid
import base64
from django.core.files.base import ContentFile
from bs4 import BeautifulSoup
from django.urls import reverse

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

def create_links_for_template(html,slug):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all("a",href=True):
        href = link["href"]
        if href == 'index.html' or href == '/':
            link["href"] = reverse('builder:template-preview', kwargs={'slug': slug})
        elif '.html' in href:
            link["href"] = reverse('builder:template-preview', kwargs={'slug': slug}) + "/" + href.replace('.html','')
    return soup.prettify()