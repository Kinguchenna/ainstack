from django import forms
from .models import CustomVoice

class CustomVoiceForm(forms.ModelForm):
    class Meta:
        model = CustomVoice
        fields = ['voice_name', 'voice_file']