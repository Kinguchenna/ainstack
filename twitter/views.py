import os
import re
import time
import uuid
import logging
import platform
import requests
import yt_dlp


from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from yt_dlp import YoutubeDL

from tts.helpers import check_internet_connectivity, check_is_video_url_connectivity
from blog.helper import blog_dynamic
from djangoML.utils import get_or_create_subscription
from youTube.utils import download_hook, get_user_key, download_progress
from account.models import UserSubscription, SubscriptionPlan
from django.contrib.auth.models import User
from account.models import DownloadHistory
# Assume these are defined somewhere in your project:
# from your_app.models import User, DownloadHistory, UserSubscription
# from your_app.utils import check_network_connection, get_client_ip, update_user_ip_01, get_or_create_sub, get_user_key, download_hook, blog_dynamic

logger = logging.getLogger(__name__)


def index(request):
        # GET request: render page
    network_status = check_network_connection()
    blogs = blog_dynamic()

    context = {
        'network_status': network_status,
        'blogs': blogs,
    }
    return render(request, "twitter/index.html", context)

def sanitize_filename(name):
    # Remove characters not safe for filenames, replace spaces with underscores
    return re.sub(r'[^a-zA-Z0-9 \-_]', '', name).strip().replace(' ', '_')


def check_network_connection():
    status = check_internet_connectivity()  # Ensure this function is defined
    return status


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For might contain multiple IPs
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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


def check_is_video_url_valid(video_url, timeout=5):
    """Validate video URL using yt_dlp"""
    try:
        yt_dlp.YoutubeDL({'quiet': True}).extract_info(video_url, download=False)
        return True
    except Exception:
        return False

# @csrf_exempt
# def twitter(request):
#     if request.method == "POST":
#         video_url = request.POST.get("video_url")

#         # Set up output filename
#         output_path = os.path.join(settings.MEDIA_ROOT, "downloads")
#         os.makedirs(output_path, exist_ok=True)

#         ydl_opts = {
#             "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
#             "format": "bestvideo+bestaudio/best",
#             "merge_output_format": "mp4",
#             "quiet": True,
#         }

#         try:
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(video_url, download=True)
#                 file_path = ydl.prepare_filename(info)

#             if not os.path.exists(file_path):
#                 return JsonResponse({"error": "Download failed. File not found."})

#             return FileResponse(open(file_path, "rb"), as_attachment=True)

#         except Exception as e:
#             return JsonResponse({"error": str(e)})

#     return JsonResponse({"error": "Invalid request method."})



@csrf_exempt
def twitter(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        video_format = request.POST.get("video_format", "mp4")

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
        subscription = get_or_create_subscription(request.user, char_count=300)
        if subscription is None:
            return JsonResponse({
                'message': 'Please <a href="/subscribe/" style="text-decoration: none; color: #0E8AB3;">Become a Member</a> - Downloads limit exceeded.'
            }, status=403)

        output_path = os.path.join(settings.MEDIA_ROOT, "downloads")
        os.makedirs(output_path, exist_ok=True)

        outtmpl = os.path.join(output_path, "%(title)s.%(ext)s")

        user_key = get_user_key(request)
                # Clear any previous progress data for this user
        download_progress.pop(user_key, None)

        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bestaudio/best" if video_format == "mp3" else "bestvideo+bestaudio/best",
            "merge_output_format": "mp4" if video_format == "mp4" else None,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }] if video_format == "mp3" else [],
            'progress_hooks': [download_hook(user_key)],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                file_path = ydl.prepare_filename(info)

                # Update extension if audio-only
                if video_format == "mp3":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"

            if not os.path.exists(file_path):
                return JsonResponse({"success": False, "message": "Download failed. File not found."})

            filename = os.path.basename(file_path)
            download_url = f"/media/downloads/{filename}"
            
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
                "success": True,
                "message": "Download complete.",
                "download_url": download_url
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Error: {str(e)}"
            })

    return JsonResponse({"success": False, "message": "Invalid request method."})




def get_twitter_progress(request):
    key = get_user_key(request)
    data = download_progress.get(key, {
        'percent': '0%',
        'speed': '0KiB/s',
        'eta': 'Unknown',
        'total': 'Unknown'
    })
    return JsonResponse(data)
