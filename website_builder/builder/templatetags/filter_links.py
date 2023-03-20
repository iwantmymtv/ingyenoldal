from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True,name="pagination_extra")
def pagination_extra(context):
    param_string=''
    value = context['current_dict']
    for k,v in value.items():
        if v['current_id']:
            param_string += f"&{k}={v['current_id']}"
    return param_string


@register.simple_tag(takes_context=True,name="filter_params")
def filter_params(context):
    param_string=''
    value = context['extra_params']
    for k,v in value.items():
        if v:
            param_string +=f"&{k}={v}"
    return param_string


@register.simple_tag(takes_context=True,name="filter_cancel")
def filter_cancel(context):
    param_string=''
    value = context['extra_params']
    for k,v in value.items():
        if v:
            param_string +=f"?{k}={v}"
        else:
            return reverse('builder:template-list')
    return param_string
