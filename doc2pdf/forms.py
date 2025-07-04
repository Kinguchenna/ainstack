from django import forms
from .models import Document

from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'url',
                'placeholder': 'Enter document title',
                'style': 'margin-bottom: 10px;'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'url',
                'style': 'margin-bottom: 10px;style=width: 30%;'
            }),
        }
