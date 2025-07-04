from django.shortcuts import render, redirect, get_object_or_404
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
from account.models import DownloadHistory
from account.models import UserSubscription, SubscriptionPlan, Payment
from .helpers import check_internet_connectivity
from djangoML.utils import get_or_create_sync_subscription, validate_safe_ssml, check_user_email_verified,parse_multi_voice_segments
from blog.helper import blog_dynamic
import json
import re
import uuid
from account.models import UserPreference
from django.contrib.auth.decorators import login_required
from pydub import AudioSegment  # You need to install pydub and ffmpeg

from googletrans import Translator as GoogleTranslator, LANGUAGES
from libretranslatepy import LibreTranslateAPI

def translate_text(request):
    translated = None
    text = request.GET.get("text")
    lang = request.GET.get("lang", "fr")
    engine = request.GET.get("engine", "google")
    print(LANGUAGES)

    if text:
        try:
            if engine == "libre":
                lt = LibreTranslateAPI("https://libretranslate.de")
                translated = lt.translate(text, "auto", lang)
                print('lt',lt.languages()) 
            else:
                translator = GoogleTranslator()
                translated = translator.translate(text, dest=lang).text
        except Exception as e:
            translated = f"Error: {str(e)}"

    return render(request, "tts/translate_form.html", {"translated": translated})

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
    network_status = False
    voices = []
    blogs = []

    try:
        voices = async_to_sync(edge_tts.list_voices)()
        network_status = check_internet_connectivity()
        blogs = blog_dynamic()  # Now works correctly
    except Exception as e:
        
        voices = []
        blogs = []

    context = {
        'voices': voices,
        'network_status': network_status,
        'blogs': blogs  # Pass blogs to your template!
    }
    print("blogs:", blogs)
    return render(request, 'tts/home.html', context)


def text_to_speach(request):
    network_status = False
    preferences = []
    voices = []
    blogs = []
    try:
        network_status = check_internet_connectivity()
        voices = async_to_sync(edge_tts.list_voices)()
        preferences, created = UserPreference.objects.get_or_create(user=request.user)
        blogs = blog_dynamic()  # Now works correctly

    except Exception as e:
        voices = []
    context = {
        'voices': voices,
        'network_status': network_status,
        'blogs': blogs,
        'preferences': preferences,
    }
    
    return render(request, 'tts/text_to_speach.html', context) 


def load_sample_voice(request):
    network_status = False
    voices = []
    blogs = []
    try:
        network_status = check_internet_connectivity()
        voices = async_to_sync(edge_tts.list_voices)()
        blogs = blog_dynamic()  # Now works correctly
    except Exception as e:
        voices = []
    context = {
        'voices': voices,
        'network_status': network_status,
        'blogs': blogs  # Pass blogs to your template!
    }
    
    return render(request, 'tts/load_sample_voice.html', context) 


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

@sync_to_async
def check_network_connection():
    status = check_internet_connectivity()  # Ensure this function is defined
    return status

@sync_to_async
def saveToDownloadHistory(video_url,user,name,email):
    history = DownloadHistory.objects.create(
                video_url = video_url,
                user = user,
                name=name,
                email=email
            )
    return history


@sync_to_async(thread_sensitive=False)
def get_free_subscription(user):
    return UserSubscription.objects.select_related('plan').get(user=user)

@sync_to_async
def count_characters(text: str) -> int:
    return len(text)

# @csrf_exempt
# @login_required
# @subscription_required

async def process_voice(request):
    voicetext = request.GET.get('text', 'sdsdsd')
    short_name = request.GET.get('ShortName', "en-US-GuyNeural")
    speed = request.GET.get('speed')
    pitch = request.GET.get('pitch')
    print("this is your balance one")

    # Reject empty text
    if not voicetext:
        return JsonResponse({'message': 'Text parameter is required.'}, status=400)
    print("this is your balance two")
    
    # Disallow SSML custom tags
    if re.search(r'<\/?speak|<voice|<prosody|<mstts:', voicetext, re.IGNORECASE):
        return JsonResponse({'message': 'Custom SSML tags are not supported.'}, status=400)
        # pass
    print("this is your balance three")

    # Check network status
    status = await check_network_connection()
    if not status:
        return JsonResponse({
            'message': 'Please check your network and try again.'
        }, status=403)
    print("this is your balance four")

    is_verified = await check_user_email_verified(request.user)
    if not is_verified:
        return JsonResponse({
            'message': 'Please verify your email and try again.'
        }, status=403)    

    # Check user authentication
    user = await check_user_is_auth(request.user)
    if not user:
        return JsonResponse({
            'message': 'Please <a href="/login" style="text-decoration: none; color: #0E8AB3;background: transparent;margin: 0 0 0;padding: 2px 2px 2px;">login</a> and come back.'
        }, status=403)
    print("this is your balance five")

    # Suspicious activity check
    ip = get_client_ip(request)
    response_message = await check_suspicious_activity(ip)
    if response_message == "Suspicious activity detected":
        return JsonResponse({'message': response_message}, status=403)
    print("this is your balance six")
    
    await update_user_ip(ip, request.user)
        
    char_count = len(voicetext) 
    
    # Check Free plan limits
    sub_free = await get_free_subscription(request.user)
    if sub_free.plan and sub_free.plan.name == "Free" and char_count > 500:
        return JsonResponse({
                'message': 'Please <a href="/subscribe/" style="text-decoration: none; color: #0E8AB3;background: transparent;margin: 0 0 0;padding: 2px 2px 2px;">Become a Memeber</a> Free Plan Limit 500 Chars.'
                }, status=403)
    print("this is your balance seven")
    
    subscription = await get_or_create_sync_subscription(request.user, char_count)
    if subscription is None:
        return JsonResponse({'message': 'Character limit exceeded'}, status=403)
    print("this is your balance eight")

    segments = parse_multi_voice_segments(voicetext)
    if not segments:
    # Generate unique filename to avoid overwrites
        filename = f"{request.user}_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
        if re.search(r'<[a-z]*:?voice|<mstts:', voicetext, re.IGNORECASE):
            if not validate_safe_ssml(voicetext):
                return JsonResponse({'message': 'Invalid or unsupported SSML structure.'}, status=400)
            communicate = edge_tts.Communicate(text=voicetext, voice=short_name)
        else:
            communicate = edge_tts.Communicate(text=voicetext, voice=short_name, rate=speed, pitch=pitch)
        await communicate.save(filepath)

        await saveToDownloadHistory(voicetext,request.user,request.user.get_full_name() or request.user.username,request.user.email)

        message = "Converted"

        return JsonResponse({
            'message': message,
            'voicetext': voicetext,
            'file_url': settings.MEDIA_URL + filename
        })
    else:
        combined_audio = AudioSegment.empty()
        filenames = []
        for idx, (voice, text) in enumerate(segments):
            print(f"[Segment {idx}] Voice: {voice} | Text: {text.strip()}")
            filename = f"{request.user}_{uuid.uuid4().hex}_{idx}.mp3"
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            print(f"[Segment {idx}] Voice: {voice.strip()} | Text: {text.strip()}")

            communicate = edge_tts.Communicate(text=text.strip(), voice=voice.strip(), rate=speed, pitch=pitch)
            await communicate.save(filepath)
            await asyncio.sleep(0.1) 

            audio = AudioSegment.from_file(filepath, format="mp3")
            combined_audio += audio
            filenames.append(filepath)

        final_filename = f"{request.user}_{uuid.uuid4().hex}_final.mp3"
        final_filepath = os.path.join(settings.MEDIA_ROOT, final_filename)
        combined_audio.export(final_filepath, format="mp3")

        # Optional: Clean up individual segment files
        for f in filenames:
            if os.path.exists(f):
                os.remove(f)

        await saveToDownloadHistory(voicetext, request.user, request.user.get_full_name() or request.user.username, request.user.email)

        return JsonResponse({
            'message': 'Converted with multi-voice segments',
            'voicetext': voicetext,
            'file_url': settings.MEDIA_URL + final_filename
        })



 

# @login_required
def preferences_view(request):
    preferences, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        preferences.preferred_voice = request.POST.get('preferred_voice', preferences.preferred_voice)
        preferences.preferred_pitch = request.POST.get('preferred_pitch', preferences.preferred_pitch)
        preferences.preferred_speed = request.POST.get('preferred_speed', preferences.preferred_speed)
        preferences.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({
        'preferred_voice': preferences.preferred_voice,
        'preferred_pitch': preferences.preferred_pitch,
        'preferred_speed': preferences.preferred_speed
    })

async def sample_voice(request):
    voicetext = request.GET.get('text', 'sdsdsd')
    short_name = request.GET.get('ShortName', "en-US-GuyNeural")
    speed = request.GET.get('speed')
    pitch = request.GET.get('pitch')
    # print("this is pitch", pitch)

    # print("Speed Voices", speed)

    # Check network status
    status = await check_network_connection()
    if not status:
        print("Status for neteok", status)
        return JsonResponse({
            'message': 'Please check your network and try again.'
        }, status=403)

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

    print("count caracter", char_count)
    # count_chars = await count_characters(voicetext) 
    # print("count_chars", count_chars)
    

    sub_free = await get_free_subscription(request.user)
    if sub_free.plan and sub_free.plan.name == "Free" and char_count > 500:
        return JsonResponse({
                'message': 'Please <a href="/subscribe/" style="text-decoration: none; color: #0E8AB3;background: transparent;margin: 0 0 0;padding: 2px 2px 2px;">Become a Memeber</a> Free Plan Limit 500 Chars.'
                }, status=403)
    
    subscription = await get_or_create_sync_subscription(request.user, char_count)
    # print("sub data new", subscription.plan)

    # subs = await subs_state(request.user)
    # print("subs_state", subs)

    if subscription is None:
        # print("Character limit exceeded")
        return JsonResponse({'message': 'Character limit exceeded'}, status=403)

    filename = "output1.mp3"
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    communicate = edge_tts.Communicate(text=voicetext, voice=short_name, rate=speed, pitch=pitch)
    await communicate.save(filepath)

    await saveToDownloadHistory(voicetext,request.user,request.user.get_full_name() or request.user.username,request.user.email)


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

def process_song(request):
    voices = []
    try:
        voices = async_to_sync(edge_tts.list_voices)()
    except Exception as e:
        voices = []
    context = {
        'voices' : voices
    }
    
    return render(request, 'tts/texttosong.html', context) 

async def texttosong(request):
    voicetext = request.GET.get('text', 'sdsdsd')
    short_name = request.GET.get('ShortName', "en-US-GuyNeural")
    pitch = request.GET.get('pitch', 'default')  # Get pitch from user input
    speed = request.GET.get('speed', 'default')  # Get speed from user input

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

    subscription = await get_or_create_sync_subscription(request.user, char_count)
    if subscription is None:
        print("Character limit exceeded")
        return JsonResponse({'message': 'Character limit exceeded'}, status=403)

    filename = "output1.mp3"
    filepath = os.path.join(settings.MEDIA_ROOT, filename) 

    # Assuming the edge_tts library supports SSML input (for melody or musicality effect)
    communicate = edge_tts.Communicate(text=voicetext, voice=short_name)
    await communicate.save(filepath)

    message = "Converted to Song-like Audio"

    return JsonResponse({
        'message': message,
        'voicetext': voicetext,
        'file_url': settings.MEDIA_URL + filename
    })




@login_required
def start_checkout(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    context = {
        'plan': plan,
        'paypal_client_id': 'AUWwAfEif6AqDZs8QEwvijjhDHV-LpxgaHhuj_WMcJCP9LWtgitXRTQXrKmWcoQXbfFlIlxBZpOPeijJ',
    }
    return render(request, 'tts/checkout.html', context)


@csrf_exempt
@login_required
def payment_complete(request):
    data = json.loads(request.body)
    plan = get_object_or_404(SubscriptionPlan, id=data['plan_id'])

    # Save payment
    Payment.objects.create(
        user=request.user,
        plan=plan,
        payment_id=data['order_id'],
        status='Paid'
    )

    # Auto-upgrade logic (e.g., extend user model or profile)
    request.user.profile.subscription_plan = plan
    request.user.profile.save()

    return JsonResponse({'status': 'ok'})







from .forms import CustomVoiceForm
from .models import CustomVoice
import subprocess



@login_required
def upload_voice(request):
    if request.method == 'POST':
        form = CustomVoiceForm(request.POST, request.FILES)
        if form.is_valid():
            voice = form.save(commit=False)
            voice.user = request.user
            voice.save()
            process_custom_voice(voice.voice_file.path)
            return redirect('dashboard')  # Redirect to user dashboard or another page
    else:
        form = CustomVoiceForm()
    return render(request, 'upload_voice.html', {'form': form})

# Background TTS Processing with Coqui

def process_custom_voice(file_path):
    output_path = file_path.replace('.wav', '_test_output.wav')
    text = "This is a test of your custom voice."  # Can be dynamic
    try:
        subprocess.run([
            'tts',
            '--text', text,
            '--speaker_wav', file_path,
            '--out_path', output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating custom voice: {e}")