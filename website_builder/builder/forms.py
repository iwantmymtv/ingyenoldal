from django.forms import ModelForm

from website_builder.builder.widgets import HtmlEditor
from website_builder.builder.models import (
    Template,
    Block
)
class TemplateAdminForm(ModelForm):
    model = Template
    class Meta:
        fields = '__all__'
        widgets = {
            'html_content': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
        }

class BlockAdminForm(ModelForm):
    model = Block
    class Meta:
        fields = '__all__'
        widgets = {
            'html_content': HtmlEditor(attrs={'style': 'width: 90%; height: 100%;'}),
        }