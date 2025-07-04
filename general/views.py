from django.shortcuts import render


from django.conf import settings
import os

def show_logs(request):
    log_path = '/home/ainstack/core/djangoML/stderr.log'  # Update to your actual log path

    logs = ""
    try:
        with open(log_path, 'r') as f:
            logs = f.read()
    except Exception as e:
        logs = f"Error reading log file: {e}"

    context = {
        'logs': logs
    }
    return render(request, 'general/show_logs.html', context)


# from django.shortcuts import render, redirect
# from .forms import CaptchaForm
# from .captcha_generator import generate_captcha_text, generate_captcha_image

# def captcha_view(request):
#     if request.method == 'POST':
#         form = CaptchaForm(request.POST)
#         if form.is_valid():
#             if form.cleaned_data['captcha'] == request.session.get('captcha_text'):
#                 request.session['is_human'] = True
#                 return redirect('protected_page')  # allow access
#             else:
#                 form.add_error('captcha', 'Incorrect CAPTCHA')
#     else:
#         form = CaptchaForm()
#         text = generate_captcha_text()
#         request.session['captcha_text'] = text
#         image_data = generate_captcha_image(text)
#         return render(request, 'general/captcha.html', {'form': form, 'image_data': image_data})

#     image_data = generate_captcha_image(request.session.get('captcha_text', ''))
#     return render(request, 'general/captcha.html', {'form': form, 'image_data': image_data})


# Create your views here.


from django.shortcuts import render, redirect
from .forms import CaptchaForm
from .captcha_generator import generate_captcha_text, generate_captcha_image
from django.utils import timezone

# def captcha_view(request):
#     next_url = request.GET.get('next', '/')
#     if request.method == 'POST':
#         form = CaptchaForm(request.POST)
#         if form.is_valid():
#             if form.cleaned_data['captcha'] == request.session.get('captcha_text'):
#                 request.session['is_human'] = True
#                 return redirect(request.POST.get('next', '/'))
#             else:
#                 form.add_error('general/captcha', 'Incorrect CAPTCHA')
#     else:
#         form = CaptchaForm()
#         text = generate_captcha_text()
#         request.session['captcha_text'] = text
#         image_data = generate_captcha_image(text)

#     return render(request, 'general/captcha.html', {
#         'form': form,
#         'image_data': image_data,
#         'next': next_url,
#     })


 
def captcha_view(request):
    next_url = request.GET.get('next', '/')
    
    if request.method == 'POST':
        form = CaptchaForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('website'):
                form.add_error('captcha', 'Incorrect CAPTCHA')
            if form.cleaned_data['captcha'] == request.session.get('captcha_text'):
                request.session['is_human'] = True
                request.session['is_human_verified_at'] = timezone.now().isoformat()
                return redirect(request.POST.get('next', '/'))
            else:
                form.add_error('captcha', 'Incorrect CAPTCHA')
        # Regenerate captcha text and image on POST (whether valid or invalid)
        text = generate_captcha_text()
        request.session['captcha_text'] = text
        image_data = generate_captcha_image(text)

    else:
        form = CaptchaForm()
        text = generate_captcha_text()
        request.session['captcha_text'] = text
        image_data = generate_captcha_image(text)

    return render(request, 'general/captcha.html', {
        'form': form,
        'image_data': image_data,
        'next': next_url,
    })




def logout_human(request):
    request.session.pop('is_human', False)
    return redirect('/')


from .decorators import human_verification_required

# @human_verification_required
def apiDocumentation(request):

    return render(request, 'general/api.html')


# @human_verification_required
def aboutus(request):
    
    return render(request, 'general/aboutus.html')


# @human_verification_required
def careers(request):
    
    return render(request, 'general/careers.html')