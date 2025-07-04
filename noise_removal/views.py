import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import AudioUploadForm
from .utils import remove_noise
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from tts.helpers import check_internet_connectivity, check_is_video_url_connectivity
from djangoML.utils import get_or_create_subscription, get_client_ip,update_user_ip_01
from account.models import UserSubscription, SubscriptionPlan
from django.contrib.auth.models import User

# You’ll need a Python audio processing library that can remove background noise. Some popular choices:

# noisereduce — simple and effective noise reduction in Python.

# pydub — for audio manipulation (format conversion, slicing).

# librosa — advanced audio processing.

# scipy — signal processing tools.

# noisereduce is great for your purpose.


# pip install django noisereduce librosa soundfile numpy

# def upload_audio(request):
#     if request.method == 'POST':
#         form = AudioUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             audio_file = form.cleaned_data['audio_file']
#             # Save original file
#             original_path = os.path.join(settings.MEDIA_ROOT, audio_file.name)
#             with open(original_path, 'wb+') as destination:
#                 for chunk in audio_file.chunks():
#                     destination.write(chunk)
            
#             # Define output path
#             cleaned_name = f"cleaned_{audio_file.name}"
#             cleaned_path = os.path.join(settings.MEDIA_ROOT, cleaned_name)

#             # Remove noise
#             remove_noise(original_path, cleaned_path)

#             # Redirect to result page
#             return HttpResponseRedirect(reverse('noise_removal:noice_result', kwargs={'filename': cleaned_name}))
#     else:
#         form = AudioUploadForm()
#     return render(request, 'noise_removal/upload.html', {'form': form})

def noice_result(request, filename):
    file_url = settings.MEDIA_URL + filename
    return render(request, 'noise_removal/result.html', {'file_url': file_url})


def check_network_connection():
    status = check_internet_connectivity()  # Ensure this function is defined
    return status




def upload_audio(request):
    return render(request, 'noise_removal/upload.html')

@csrf_exempt  # Remove this if CSRF token is handled in JS
def post_upload_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')  # ✅ Correct way to access the uploaded file
        if audio_file:

            if not check_network_connection():
                return JsonResponse({'error': 'Please check your network and try again.'}, status=403)

            if not request.user.is_authenticated:
                return JsonResponse({
                    'error': 'Please <a href="/login" style="text-decoration: none; color: #0E8AB3;">login</a> and come back.'
                }, status=403)
            

            ip = get_client_ip(request)
            response_message = UserSubscription.check_suspicious_activity(ip)
            if response_message == "Suspicious activity detected":
                return JsonResponse({'error': response_message}, status=403)

            update_user_ip_01(ip, request.user)

            if not audio_file or not audio_file:
                return JsonResponse({'success': False, 'error': 'URL and format are required'}, status=400)


            download_used = 1000
            subscription = get_or_create_subscription(request.user, char_count=250)
            if subscription is None:
                return JsonResponse({
                    'error': 'Please <a href="/subscribe/" style="text-decoration: none; color: #0E8AB3;">Become a Member</a> - Downloads limit exceeded.'
                }, status=403)
        
            original_path = os.path.join(settings.MEDIA_ROOT, audio_file.name)
            with open(original_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            cleaned_name = f"cleaned_{audio_file.name}"
            cleaned_path = os.path.join(settings.MEDIA_ROOT, cleaned_name)

            try:
                remove_noise(original_path, cleaned_path)

                return JsonResponse({
                    'success': True,
                    'filename': cleaned_name,
                    'url': f"/media/{cleaned_name}"
                })
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

        return JsonResponse({'success': False, 'error': 'No audio file uploaded.'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)