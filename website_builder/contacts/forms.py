from django.forms import ModelForm
from website_builder.contacts.models import Contact

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ['user']
