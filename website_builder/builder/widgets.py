from django import forms

class HtmlEditor(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(HtmlEditor, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'html-editor'

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/codemirror.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/codemirror.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/xml/xml.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.9.0/mode/htmlmixed/htmlmixed.js',
            'https://firebasestorage.googleapis.com/v0/b/landing-web-b6d34.appspot.com/o/valami%2Finit.js?alt=media&token=0e9d6926-bb9f-4437-ae70-7e6f678c244e'
        )