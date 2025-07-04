from account.models import UserSubscription, SubscriptionPlan, EmailVerification
from asgiref.sync import sync_to_async
import requests
import re



from django.utils import timezone

def ensure_active_subscription(user):
    subscription, created = UserSubscription.objects.get_or_create(user=user)
    now = timezone.now()

    # Assign default plan if none exists
    if subscription.plan is None:
        default_plan, _ = SubscriptionPlan.objects.get_or_create(
            name="Free",
            defaults={
                'character_limit': 3500,
                'price': 0
            }
        )
        subscription.plan = default_plan

        if subscription.promo == 0:
            subscription.limit = default_plan.character_limit
            subscription.balance = default_plan.character_limit
            subscription.promo = 1
            subscription.last_updated = now
            subscription.save()

    # Check if subscription is active for the current month
    if not subscription.last_updated or \
       subscription.last_updated.month != now.month or \
       subscription.last_updated.year != now.year:
        return None  # No active subscription for the current month
    
        # Check if the plan is specifically for "Survey"
    if not subscription.plan.name.lower().__contains__("survey"):
        return None  # Not a Survey plan

    return subscription



def check_internet_connectivity(url="https://www.google.com", timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.RequestException:
        return False


def get_or_create_subscription(user, char_count):
    subscription, created = UserSubscription.objects.get_or_create(user=user)

    # Assign default plan if none exists
    if subscription.plan is None:
        default_plan, _ = SubscriptionPlan.objects.get_or_create(
            name="Free",
            defaults={
                'character_limit': 3500,
                'price': 0
            }
        )
        subscription.plan = default_plan

        # if user have not used free promo before
        if subscription.promo == 0:
            subscription.limit = default_plan.character_limit
            subscription.balance = default_plan.character_limit
            subscription.promo = 1

        subscription.save()

    # Check if user has enough characters
    if subscription.remaining_characters() < char_count:
        return None

    # Deduct character count and save
    print("characters_used", subscription.characters_used)
    subscription.characters_used += char_count
    subscription.promo = 1
    print("char_count", char_count)

    print("current  balance", max(0, subscription.balance - char_count))
    # subscription.balance = subscription.plan.character_limit - subscription.characters_used
    subscription.balance = max(0, subscription.balance - char_count)
    # print("this is your balance check utils", (subscription.plan.character_limit - subscription.characters_used))

    subscription.save()

    return subscription



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



@sync_to_async
def get_or_create_sync_subscription(user, char_count):
    subscription, created = UserSubscription.objects.get_or_create(user=user)

    # Assign default plan if none exists
    if subscription.plan is None:
        default_plan, _ = SubscriptionPlan.objects.get_or_create(
            name="Free",
            defaults={
                'character_limit': 3500,
                'price': 0
            }
        )
        subscription.plan = default_plan

        # if user have not used free promo before
        if subscription.promo == 0:
            subscription.limit = default_plan.character_limit
            subscription.balance = default_plan.character_limit
            subscription.promo = 1

        subscription.save()

    # Check if user has enough characters
    if subscription.remaining_characters() < char_count:
        return None

    # Deduct character count and save
    print("characters_used", subscription.characters_used)
    subscription.characters_used += char_count
    subscription.promo = 1
    print("char_count", char_count)

    print("char_count from balance", max(0, subscription.balance - char_count))
    # subscription.balance = subscription.plan.character_limit - subscription.characters_used
    subscription.balance = max(0, subscription.balance - char_count)
    print("this is your balance check utils", (subscription.plan.character_limit - subscription.characters_used))

    subscription.save()

    return subscription


# @sync_to_async
# def check_user_email_verified(user):
#     is_verified = True
#     verification = EmailVerification.objects.get(user=user)
#     if verification.is_verified:
#         is_verified = True
#     else:
#         is_verified = False
#     return is_verified


from account.models import EmailVerification
from asgiref.sync import sync_to_async

@sync_to_async
def check_user_email_verified(user):
    try:
        verification = EmailVerification.objects.get(user=user)
        return verification.is_verified
    except EmailVerification.DoesNotExist:
        return False  # Or True, depending on how you want to treat users without a record






import xml.etree.ElementTree as ET

def validate_safe_ssml(ssml_text):
    try:
        # Parse to ensure it's well-formed XML
        root = ET.fromstring(ssml_text.strip())

        # Set of allowed tags (namespace prefix is removed in check)
        allowed_tags = {
            'speak', 'voice', 'prosody',
            'express-as', 'viseme', 'backgroundaudio',
            'silence', 'audioduration', 'styledegree', 'emotion',
            'dialog', 'turn'  # <mstts:dialog> and <mstts:turn>
        }

        # Recursively validate tag names
        for elem in root.iter():
            tag = elem.tag.lower()
            if ":" in tag:
                tag = tag.split(":", 1)[1]  # strip namespace
            if tag not in allowed_tags:
                return False

        return True

    except ET.ParseError:
        return False
    

def check_if_user_is_auth(user):
    if user.is_authenticated:
        return True
    else:
        return False



def parse_multi_voice_segments(text):
    pattern = r'\[(.*?)\]:\s*((?:.|\n)*?)(?=(?:\n\[|$))'
    return re.findall(pattern, text.strip())