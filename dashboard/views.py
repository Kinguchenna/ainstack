from django.shortcuts import render
from tts.helpers import check_internet_connectivity
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from djangoML.utils import check_if_user_is_auth
from django.shortcuts import redirect
from django.contrib.auth.models import User
from  account.models import DownloadHistory
from account.models import UserSubscription, SubscriptionPlan
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import JsonResponse

# Create your views here.
# @login_required
def dashboard(request):
    # print('request.path',request.path)
    user = check_if_user_is_auth(request.user)
    if user:
        network_status = False
        balance = 0
        total_user = 0
        visitors = 0
        users = []
        downloads = []
        try:
            network_status = check_internet_connectivity()
            total_user = User.objects.count()
            users = User.objects.all()
            subscription = UserSubscription.objects.filter(user=request.user).first()
            downloads = DownloadHistory.objects.filter(user=request.user).order_by('-downloaded_at')
            if subscription:
                balance = subscription.balance
            else:
                balance = 0            
        except Exception as e:
            voices = []
            users = []
            downloads = []
        context = {
            'network_status': network_status,
            'total_user': total_user,
            'balance': balance,
            'users': users,
            'downloads': downloads,
        }
        return render(request, 'dashboard/index.html', context) 
    else:
        return redirect('login')
    

def downloads(request):
    # print('request.path',request.path)
    user = check_if_user_is_auth(request.user)
    if user:
        network_status = False
        balance = 0
        total_user = 0
        visitors = 0
        users = []
        downloads = []
        try:
            network_status = check_internet_connectivity()
            total_user = User.objects.count()
            users = User.objects.all()
            subscription = UserSubscription.objects.filter(user=request.user).first()
            downloads = DownloadHistory.objects.filter(user=request.user).order_by('-downloaded_at')
            # DownloadHistory.objects.filter(user=request.user).delete()
            if subscription:
                balance = subscription.balance
            else:
                balance = 0
                downloads = []            
        except Exception as e:
            voices = []
            users = []
        context = {
            'network_status': network_status,
            'total_user': total_user,
            'balance': balance,
            'users': users,
            'downloads': downloads,
        }
        return render(request, 'dashboard/downloads.html', context) 
    else:
        return redirect('login')
    




def transfer(request):
    # print('request.path',request.path)
    user = check_if_user_is_auth(request.user)
    if user:
        network_status = False
        balance = 0
        total_user = 0
        visitors = 0
        users = []
        downloads = []
        try:
            network_status = check_internet_connectivity()
            total_user = User.objects.count()
            users = User.objects.exclude(id=request.user.id)
            subscription = UserSubscription.objects.filter(user=request.user).first()
            downloads = DownloadHistory.objects.filter(user=request.user).order_by('-downloaded_at')
            # DownloadHistory.objects.filter(user=request.user).delete()
            if subscription:
                balance = subscription.balance
            else:
                balance = 0
                downloads = []            
        except Exception as e:
            voices = []
            users = []
        context = {
            'network_status': network_status,
            'total_user': total_user,
            'balance': balance,
            'users': users,
            'downloads': downloads,
        }
        return render(request, 'dashboard/transfer.html', context) 
    else:
        return redirect('login')
    

# CSRF protection is not exempt in this case
@csrf_protect
def transfer_to(request):
    if request.method == "POST":
        username = request.POST.get("to")
        amount = int(request.POST.get("amount", 0))
        info = request.POST.get("info")

        try:
            to_user = User.objects.get(username=username)
            sender_sub = UserSubscription.objects.get(user=request.user)
            receiver_sub = UserSubscription.objects.get(user=to_user)

            if sender_sub.balance >= amount:
                sender_sub.balance -= amount
                receiver_sub.balance += amount
                sender_sub.save()
                receiver_sub.save()

                return JsonResponse({'message': f'Transferred {amount} credits to {username}', 'new_balance': sender_sub.balance})
            else:
                return JsonResponse({'message': 'Insufficient balance'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=400)
    return JsonResponse({'message': 'Invalid request'}, status=400)




def verify(request):
    # print('request.path',request.path)
    user = check_if_user_is_auth(request.user)
    if user:
        network_status = False
        is_verified = False
        balance = 0
        total_user = 0
        visitors = 0
        users = []
        downloads = []
        try:
            network_status = check_internet_connectivity()
            total_user = User.objects.count()
            users = User.objects.exclude(id=request.user.id)
            subscription = UserSubscription.objects.filter(user=request.user).first()
            verification = EmailVerification.objects.get(user=request.user)
            downloads = DownloadHistory.objects.filter(user=request.user).order_by('-downloaded_at')
            # DownloadHistory.objects.filter(user=request.user).delete()
            if subscription:
                balance = subscription.balance
            else:
                balance = 0
                downloads = []      
            if verification.is_verified:
                is_verified = True
            else:
                is_verified = False

        except Exception as e:
            voices = []
            users = []
        context = {
            'network_status': network_status,
            'total_user': total_user,
            'balance': balance,
            'users': users,
            'downloads': downloads,
            'is_verified': is_verified,
        }
        return render(request, 'dashboard/verifyemail.html', context) 
    else:
        return redirect('login')
    

# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from account.models import EmailVerification


# CSRF protection is not exempt in this case
import uuid

@csrf_protect
def verify_account(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    token = request.POST.get("token")

    if not token:
        return JsonResponse({'error': 'Token is required.'}, status=400)

    try:
        token_uuid = uuid.UUID(token)
    except ValueError:
        return JsonResponse({'error': 'Invalid token format. Token must be a valid UUID.'}, status=400)

    try:
        verification = EmailVerification.objects.get(token=token_uuid, user=request.user)
    except EmailVerification.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired verification token.'}, status=404)

    if verification.is_verified:
        return JsonResponse({'message': 'Email already verified.'}, status=200)

    if verification.is_expired():
        return JsonResponse({'error': 'Verification link has expired.'}, status=400)

    # Mark as verified
    verification.is_verified = True
    verification.save()

    return JsonResponse({'message': 'Your email has been verified successfully.'}, status=200)





from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import uuid
import logging



logger = logging.getLogger(__name__)  # Log errors to Django log file

 
 
 
from django.utils import timezone
 
 

@login_required
def resend_verification_email(request):
    if request.method == "POST":
        user = request.user
        
        # Get or create verification token for the user
        verification, created = EmailVerification.objects.get_or_create(user=user)

        # If the email is already verified
        if verification.is_verified:
            return JsonResponse({'message': 'Email already verified.'}, status=400)

        # If the token is expired, generate a new one
        if not created and verification.is_expired():
            verification.token = uuid.uuid4()
            verification.created_at = timezone.now()
            verification.save()

        # Compose the verification email
        verification_link = f"https://www.google.com/"
        subject = 'Verify Your Email Address'
        message = (
            f"Hi {user.username},\n\n"
            f"Please verify your email by clicking the link below:\n"
            f"{verification_link}\n\n"
            f"This link will expire in 24 hours.\n\n"
            f"If you did not request this, please ignore this email."
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
        except BadHeaderError:
            return JsonResponse({'error': 'Invalid header found.'}, status=500)
        except Exception as e:
            # Log the error for debugging purposes
            logger.exception("Email sending failed.")
            return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)

        return JsonResponse({'message': 'Verification email sent successfully.'})

    # If the request is not POST
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

    
    
    
    