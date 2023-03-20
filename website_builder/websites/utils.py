import os,requests
import tempfile
from PIL import Image
from io import BytesIO

from django.utils import timezone
from django.conf import settings
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django_hosts.resolvers import reverse as hosts_reverse

from website_builder.websites.models import Website,WebsiteExtraPage
from website_builder.websites.aws import S3

def add_action_to_forms(forms,private_uuid):
    for index,form in enumerate(forms):
        form['id'] = f"form_{index+1}"
        form_endpoint = hosts_reverse(
            'contacts:builder-form',
            kwargs={'uuid':private_uuid},
            host="default-website")
        if settings.DEBUG:
            form['action'] = 'http://localhost:8000' + form_endpoint[5:]
        else:
            form['action'] = 'https://ingyenoldal.hu' + form_endpoint[5:]
    return forms

def compile_extra_page(page:WebsiteExtraPage) -> WebsiteExtraPage:
    soup = BeautifulSoup(page.html_content, 'html.parser')
    forms = soup.find_all('form')
    
    if len(forms) > 0:
        add_action_to_forms(forms,page.website.private_uuid)
        
    page.html_content = soup.prettify()
    
    return page

def compile_website(website:Website) -> dict:
    soup = BeautifulSoup(website.html_content, 'html.parser')
    show_footer = True

    for script in soup.find_all("script"):
        script.decompose()

    forms = soup.find_all('form')
    if len(forms) > 0:
        add_action_to_forms(forms,website.private_uuid)

    #add footer if user is not subscribed
    if website.user.has_subscription() and website.user.get_subscription_end_date() > timezone.now():
        show_footer = False

    ctx = {
        "website":website,
        "styles":website.template.styles.all(),
        "scripts":website.template.scripts.all(),
        "html":soup.prettify(),
        "show_footer":show_footer
    }
    return ctx

def download_images(soup:BeautifulSoup) -> list:
    images = []
    for i in soup.find_all("img"):
        src = i['src']
        if settings.DEBUG and not 'http' in src:
            src = f'http://www.localhost:8000{src}'
        img_res = requests.get(src)
        pimg = Image.open(BytesIO(img_res.content))

        img_name = os.path.split(src)[1]
        images.append({
            'name':img_name,
            'format':pimg.format,
            'image': img_res.content
            }
        )
        i["src"] = f"images/{img_name}.{pimg.format}"

    return images

def add_html_to_links(soup):
    for link in soup.find_all("a",href=True):
        #only if a link looks like this /somting
        if not 'http' in link['href'] and not link['href'].endswith('.html') and not link['href'].startswith("#"):
            if link['href'] == "/":
                link['href'] = "index.html"
            else:
                link['href'] = f"{link['href']}.html"[1:]
    return soup

def get_rendered_html_from_template(request,website,page=None,styles=None,scripts=None):
    soup = BeautifulSoup(website.html_content, 'html.parser')
    soup = add_html_to_links(soup)
    
    #if its a page dont download main images
    if page:
        images = None
    else:
        images = download_images(soup)

    #if its a website than styles are in obj.template 
    if hasattr(website, 'template'):
        t = website.template
        styles = t.styles.all()
        scripts = t.scripts.all()
    else:
        styles = website.styles.all()
        scripts = website.scripts.all()

    ctx = {
        "website":website,
        "styles": styles,
        "scripts": scripts,
        "html":soup.prettify(),
        "show_footer":not request.user.has_subscription()
    }
    if page:
        page_soup = BeautifulSoup(page.html_content, 'html.parser')
        page_soup = add_html_to_links(page_soup)
        page.html_content = page_soup.prettify()
        ctx['page'] = page
        images = download_images(page_soup)


    index = get_template("websites/index.html")
    html  = index.render(ctx)

    res = {
        "html":html,
        "images":images
    }
    return res

def get_website_if_subscribed(request,uuid):
    if request.user.has_subscription():
        try:
            website = get_object_or_404(
                    Website,
                    private_uuid=uuid,
                    user=request.user
                )
            return website
        except:
            return None
    else:
        return None

def upload_html_to_s3(request,website,bucket_name,region):
    html = get_rendered_html_from_template(request,website)

    s3 = S3(region,bucket_name)

    fd, path = tempfile.mkstemp(suffix = '.html')
    # use a context manager to open the file at that path and close it again
    with open(path, 'w') as f:
        f.write(html)
        print(f)

    s3.upload_file(path,'index.html')
        # close the file descriptor
    os.close(fd)


def get_identifier_from_subdomain(request):
    url = request.META['HTTP_HOST']
    parse = urlparse(str(url))
    uuid = parse.path.split('.')[0]
    return uuid

def remove_template_slug_from_links(html,template_slug):
    soup = BeautifulSoup(html, 'html.parser')
    slug = hosts_reverse(
        'builder:template-preview', 
        kwargs={'slug': template_slug},
        host="default-website")[5:]
    
    for link in soup.find_all("a",href=True):
        if slug in link['href']:
            link['href'] = link['href'].replace(slug,'')
        if link['href'] == '':
            link['href'] = '/'
    
    return soup.prettify()