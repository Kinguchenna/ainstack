from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import whisper
import shutil
import tempfile
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from djangoML.utils import get_client_ip, update_user_ip_01, check_internet_connectivity,  get_or_create_subscription
from account.models import UserSubscription
from blog.helper import blog_dynamic
# Set ffmpeg binary path manually before Whisper is used
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

# Load Whisper model once globally
model = whisper.load_model("base")  # You can use "tiny", "small", etc.

def is_ffmpeg_available():
    return shutil.which("ffmpeg") is not None

def check_network_connection():
    status = check_internet_connectivity()  # Ensure this function is defined
    return status

@csrf_exempt
def transcribe_audio(request):
        # Always check network and blogs
    network_status = check_internet_connectivity()
    blogs = blog_dynamic()

    if not request.user.is_authenticated:
        return JsonResponse({
                'error': 'Please <a href="/login" style="text-decoration: none; color: #0E8AB3;">login</a> and come back.'
                }, status=403)
    
                # Check network status
    status =  check_network_connection()
    if not status:
            return JsonResponse({
                'message': 'Please check your network and try again.'
            }, status=403)

    if request.method == 'POST' and request.FILES.get('audio'):
        if not is_ffmpeg_available():
            return JsonResponse({"error": "FFmpeg is not installed or not found in PATH."}, status=500)
        
        ip = get_client_ip(request)
        response_message =  UserSubscription.check_suspicious_activity(ip)
        if response_message == "Suspicious activity detected":
            return JsonResponse({'message': response_message}, status=403)
        
        update_user_ip_01(ip, request.user)
        
        download_used = 500
        subscription = get_or_create_subscription(request.user, char_count=200)
        if subscription is None:
                print("Adio Downloads limit exceeded")
                return JsonResponse({
                'error': 'Limit exceeded.'
                }, status=403) 

        try:
            audio_file = request.FILES['audio']

            # Save file to a temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                for chunk in audio_file.chunks():
                    temp_audio.write(chunk)
                temp_audio_path = temp_audio.name

            # Transcribe using Whisper
            result = model.transcribe(temp_audio_path)

            # Clean up
            os.remove(temp_audio_path)

            return JsonResponse({"text": result['text']})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request. Make sure you're sending an audio file."}, status=400)


def audio2text(request):

        # Always check network and blogs
    network_status = check_internet_connectivity()
    blogs = blog_dynamic()

    context = {
        'network_status': network_status,
        'blogs': blogs,
    }
    return render(request, 'audio2text/index.html', context)

 