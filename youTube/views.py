from django.shortcuts import render, redirect
from django.http import JsonResponse
import asyncio
import edge_tts
from asgiref.sync import async_to_sync
import os
from django.conf import settings
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async
from django.http import HttpResponse
import tempfile
import re
from account.models import DownloadHistory
import yt_dlp
import uuid

from tts.helpers import check_internet_connectivity, check_is_video_url_connectivity
from blog.helper import blog_dynamic
from djangoML.utils import get_or_create_subscription
from .utils import download_hook, get_user_key, download_progress

from pytube import YouTube
from django.utils.text import slugify
from account.models import UserSubscription, SubscriptionPlan

def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        try:
            subscription = UserSubscription.objects.get(user=user)
        except UserSubscription.DoesNotExist:
            return JsonResponse({'message': 'No active subscription'}, status=403)

        if not subscription.is_active():
            return JsonResponse({'message': 'Subscription expired'}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper


def tts(request):
    voices = []
    try:
        voices = async_to_sync(edge_tts.list_voices)()
    except Exception as e:
        voices = []
    context = {
        'voices' : voices
    }
    
    return render(request, 'tts/index.html', context) 


def supported_voices(request):
    voices = []
    try:
        voices = async_to_sync(edge_tts.list_voices)()
    except Exception as e:
        voices = []
    context = {
        'voices' : voices
    }
    
    return render(request, 'tts/supported_voices.html', context) 

def check_network_connection():
    status = check_internet_connectivity()  # Ensure this function is defined
    return status


@sync_to_async
def update_characters_used(subscription, char_count):
    subscription.characters_used += char_count
    subscription.save()


@sync_to_async
def check_suspicious_activity(ip):
    return UserSubscription.check_suspicious_activity(ip)

@sync_to_async
def update_user_ip(ip, user):
    subscription, _ = UserSubscription.objects.get_or_create(user=user)
    subscription.ip_address = ip
    subscription.save()
@sync_to_async
def check_user_is_auth(user):
    user = user.is_authenticated
    return user

# @csrf_exempt
# @login_required
# @subscription_required

async def process_voice(request):
    voicetext = request.GET.get('text', 'sdsdsd')
    short_name = request.GET.get('ShortName', "en-US-GuyNeural")
    pitch = request.GET.get('pitch','default')
    speed = request.GET.get('speed','default')  

    user = await check_user_is_auth(request.user)
    if not user:
        return JsonResponse({
            'message': 'Please <a href="/login" style="text-decoration: none; color: #0E8AB3;background: transparent;margin: 0 0 0;padding: 2px 2px 2px;">login</a> and come back.'
        }, status=403)

    
    ip = get_client_ip(request)
    response_message = await check_suspicious_activity(ip)
    if response_message == "Suspicious activity detected":
        return JsonResponse({'message': response_message}, status=403)
    
    await update_user_ip(ip, request.user)
        
    char_count = len(voicetext) 

    subscription = await get_or_create_subscription(request.user, char_count)
    # print("sub data", subscription)
    if subscription is None:
        print("Character limit exceeded")
        return JsonResponse({'message': 'Character limit exceeded'}, status=403)

    filename = "output1.mp3"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)


    communicate = edge_tts.Communicate(text=voicetext, voice=short_name)
    await communicate.save(filepath)

    message = "Converted"

    return JsonResponse({
        'message': message,
        'voicetext': voicetext,
        'file_url': settings.MEDIA_URL + filename
    })



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For might contain multiple IPs
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def process_youdownload(request):
    voices = []
    try:
        voices = async_to_sync(edge_tts.list_voices)()
    except Exception as e:
        voices = []

    network_status = check_internet_connectivity()
    blogs = blog_dynamic()

    context = {
        'voices' : voices,
        'network_status': network_status,
        'blogs': blogs,
    }
    
    return render(request, 'tts/youdownload.html', context) 




import traceback

# Optional: create a MEDIA folder if not exists
DOWNLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def normalize_youtube_url(url):
    if "youtube.com/shorts/" in url:
        video_id = url.split("/shorts/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


# def sanitize_filename(title):
#     safe_title = re.sub(r'[^\w\s-]', '', title)
#     safe_title = re.sub(r'[-\s]+', '_', safe_title.strip())
#     # return f"{safe_title}_{uuid.uuid4().hex[:8]}"
#     return f"{safe_title}_{uuid.uuid4().hex[:8]}.webm"

def sanitize_filename(name):
    """Remove unsafe characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", slugify(name))


    
def update_user_ip_01(ip, user):
    subscription, _ = UserSubscription.objects.get_or_create(user=user)
    subscription.ip_address = ip
    subscription.save()


def get_or_create_sub(user, char_count):
    try:
        subscription = UserSubscription.objects.get(user=user)
    except UserSubscription.DoesNotExist:
        return None

    if subscription.remaining_characters() < char_count:
        return None

    return subscription

from django.contrib.auth.models import User


@sync_to_async
def subs_state(user):
    return  UserSubscription.objects.get(user=user)

def check_is_video_url_valid(video_url, timeout=5):
    """Validate video URL using yt_dlp"""
    try:
        yt_dlp.YoutubeDL({'quiet': True}).extract_info(video_url, download=False)
        return True
    except Exception:
        return False


import os
import uuid
import time
import socket
import logging

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import User
import yt_dlp

logger = logging.getLogger(__name__)

# Set global download timeout
socket.setdefaulttimeout(30)

@csrf_exempt
def youdownload(request):
    if request.method == 'POST':
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            print(f"Username: {user.username}, Email: {user.email}")

        video_url = request.POST.get('video_url')
        video_format = request.POST.get('video_format')

        if not check_network_connection():
            return JsonResponse({'message': 'Please check your network and try again.'}, status=403)

        if not request.user.is_authenticated:
            return JsonResponse({
                'message': 'Please <a href="/login" style="text-decoration: none; color: #0E8AB3;">login</a> and come back.'
            }, status=403)

        ip = get_client_ip(request)
        response_message = UserSubscription.check_suspicious_activity(ip)
        if response_message == "Suspicious activity detected":
            return JsonResponse({'message': response_message}, status=403)

        update_user_ip_01(ip, request.user)

        if not video_url or not video_format:
            return JsonResponse({'success': False, 'message': 'URL and format are required'}, status=400)

        if not check_is_video_url_valid(video_url):
            return JsonResponse({'message': 'URL does not exist or is not a valid video.'}, status=403)

        download_used = 1000
        subscription = get_or_create_subscription(request.user, char_count=500)
        if subscription is None:
            return JsonResponse({
                'message': 'Please <a href="/subscribe/" style="text-decoration: none; color: #0E8AB3;">Become a Member</a> - Downloads limit exceeded.'
            }, status=403)

        format_options = {
            'mp4': 'bestvideo+bestaudio/best',
            'mp4-low': 'worstvideo+worstaudio/worst',
            'mp4-720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'mp4-480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            'webm': 'bestvideo+bestaudio/best',
            'bestaudio': 'bestaudio',
        }

        if video_format not in format_options:
            return JsonResponse({'success': False, 'message': 'Invalid format selected'}, status=400)

        download_folder = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(download_folder, exist_ok=True)


        # Extract info first (without downloading)
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_title = sanitize_filename(info.get('title', 'video'))

        random_name = video_title
        ext = 'webm' if 'webm' in video_format else 'mp4'
        output_filename = f"{random_name}.{ext}"
        output_path = os.path.join(download_folder, output_filename)
        user_key = get_user_key(request)
                # Clear any previous progress data for this user
        download_progress.pop(user_key, None)

        ydl_opts = {
            'format': format_options[video_format],
            'outtmpl': output_path,
            'merge_output_format': ext,
            'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',  # Update path if not on Windows
            'noplaylist': True,
            'quiet': True,
            'progress_hooks': [download_hook(user_key)],
        }

        # Retry logic
        MAX_RETRIES = 3
        RETRY_DELAY = 5  # seconds

        for attempt in range(MAX_RETRIES):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                break  # Success
            except Exception as e:
                logger.error("Download attempt %s failed: %s", attempt + 1, str(e), exc_info=True)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Download failed after multiple attempts. Try again later.'
                    }, status=500)

        download_url = f"{settings.MEDIA_URL}downloads/{output_filename}"

                # Save download history
        try:
            DownloadHistory.objects.create(
                video_url=video_url,
                file=download_url,
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                email=request.user.email
            )
            print("saving user")
        except Exception as db_err:
            logger.error("Error saving download history: %s", str(db_err), exc_info=True)


        return JsonResponse({
            'success': True,
            'video_title': random_name,
            'download_url': download_url
        })

    # GET request: render page
    network_status = check_network_connection()
    blogs = blog_dynamic()

    context = {
        'network_status': network_status,
        'blogs': blogs,
    }

    return render(request, 'tts/youdownload.html', context)



def get_download_progress(request):
    key = get_user_key(request)
    data = download_progress.get(key, {
        'percent': '0%',
        'speed': '0KiB/s',
        'eta': 'Unknown',
        'total': 'Unknown'
    })
    return JsonResponse(data)




def delete_file(request):
    if request.method == 'POST':
        file_path = request.POST.get('file_path')

        try:
            # Delete the file from the server
            os.remove(file_path)
            return JsonResponse({'success': True, 'message': 'File deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
     