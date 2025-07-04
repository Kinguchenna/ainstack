from django import forms

class CaptchaForm(forms.Form):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    captcha = forms.CharField(max_length=10, label='Enter CAPTCHA')
