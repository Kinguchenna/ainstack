from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from account.models import UserSubscription, SubscriptionPlan, Payment
# Create your views here.
import json
from tts.views import get_client_ip
from asgiref.sync import async_to_sync
import edge_tts
from django.utils import timezone
from decimal import Decimal
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages




@csrf_exempt
@login_required
def subscribe_free(request, plan_name):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    user = request.user    
            # If the user has already used the free promo, they cannot use it again
    if not user:
        return JsonResponse({'error': "You Do Not Have An Account With Us Yet! Sign Up."})
    
    plan = get_object_or_404(SubscriptionPlan, name__iexact=plan_name)
    ip = get_client_ip(request)

    try:
        subscription, created = UserSubscription.objects.get_or_create(user=user)

        # If the user has already used the free promo, they cannot use it again
        if subscription.promo == 1 and plan.name == "Free":
            return JsonResponse({'error': "You have already used your free promo or there is a network error."})

        # Calculate new balance
        remaining_balance = subscription.balance if subscription.balance > 0 else 0
        new_limit = plan.character_limit
        new_balance = remaining_balance + new_limit

        # Update subscription with new plan details
        subscription.plan = plan
        subscription.promo = 1  # Mark as used promo
        subscription.characters_used = 0  # Optional: reset characters used
        subscription.limit = new_limit
        subscription.balance = new_balance
        subscription.ip_address = ip
        subscription.start_date = timezone.now()  # Set the start date to now
        subscription.save()

        return JsonResponse({'message': f"You're now subscribed to {plan.name}!"})

    except Exception as e:
        return JsonResponse({'error': f"Subscription failed: {str(e)}"}, status=500)
    



import os
import requests
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def subscribe_user(request, plan_name):
    # IPN SECRETE KEY : WvdrTUR5ygyNQS7Gb7GcnR9twwB76//Q
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    user = request.user

    # Ensure user exists in DB
    if not user:
        return JsonResponse({'error': "You do not have an account with us yet. Please sign up."})

    plan = get_object_or_404(SubscriptionPlan, name__iexact=plan_name)
    ip = get_client_ip(request)

    # Payment data to be sent to the API
    payment_data = {
        "price_amount": float(plan.price),  # assumes your plan model has a price field
        "price_currency": "usd",
        "order_id": f"{user.username}-{timezone.now().timestamp()}",
        "order_description": f"{plan.name} subscription for {user.username}",
        "ipn_callback_url": "http://127.0.0.1:8000/payment/webhook/",  # replace with actual IPN URL
        "success_url": "http://127.0.0.1:8000/success",
        "cancel_url": "http://127.0.0.1:8000/cancel"
    }

    api_key = os.getenv('INDYPAYMENTS_API_KEY')
    # print('api_key',api_key)
    payment_url = 'https://api.nowpayments.io/v1/invoice'

    try:
        # Make the payment request
        response = requests.post(
            payment_url,
            json=payment_data,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
            }
        )

        data = response.json()
        print('Full Response:', data)
        if response.status_code == 200 and 'invoice_url' in data and plan:
            
            # Get or create user subscription
            subscription, created = UserSubscription.objects.get_or_create(user=user)

            # Prevent abuse of free promo
            if subscription.promo == 1 and plan.name.lower() == "free":
                return JsonResponse({'error': "You have already used your free promo."})

            # Update subscription details
            # remaining_balance = max(subscription.balance, 0)
            # new_limit = plan.character_limit
            # new_balance = remaining_balance + new_limit

            # subscription.plan = plan
            # subscription.promo = 1 if plan.name.lower() == "free" else subscription.promo
            # subscription.characters_used = 0
            # subscription.limit = new_limit
            # subscription.balance = new_balance
            # subscription.ip_address = ip
            # subscription.start_date = timezone.now()
            # subscription.save()
            save_payment_to_db(data,user,plan)

            # Optionally redirect to invoice URL
            # return HttpResponseRedirect(data['invoice_url'])

            return JsonResponse({'message': f"Plan Name: {plan.name}!",'invoice_url': data['invoice_url'],'invoice_id': data['id']})
        else:
            return JsonResponse({'error': 'Failed to create payment', 'details': data}, status=400)

    except Exception as e:
        return JsonResponse({'error': 'Server error', 'details': str(e)}, status=500)
    

def save_payment_to_db(response_data, user, plan=None):
    payment = Payment.objects.create(
        user=user,
        plan=plan,
        payment_id=response_data.get('id'),
        token_id=response_data.get('token_id'),
        order_id=response_data.get('order_id'),
        order_description=response_data.get('order_description', ''),
        price_amount=Decimal(response_data.get('price_amount', '0')),
        # price_currency=response_data.get('price_currency', ''),
        # pay_currency=response_data.get('pay_currency') or '',
        # invoice_url=response_data.get('invoice_url'),
        # success_url=response_data.get('success_url'),
        # cancel_url=response_data.get('cancel_url'),
        # ipn_callback_url=response_data.get('ipn_callback_url'),
        # customer_email=response_data.get('customer_email') or None,
        # partially_paid_url=response_data.get('partially_paid_url') or None,
        # payout_currency=response_data.get('payout_currency') or '',
        # is_fixed_rate=response_data.get('is_fixed_rate', False),
        # is_fee_paid_by_user=response_data.get('is_fee_paid_by_user', False),
        # source=response_data.get('source') or '',
        # collect_user_data=response_data.get('collect_user_data', False),
        created_at=parse_datetime(response_data.get('created_at')),
        updated_at=parse_datetime(response_data.get('updated_at')),
        status='Pending'  # You can update this later via webhook or after confirmation
    )
    payment.save()




@csrf_exempt
def payment_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        payload = json.loads(request.body)
        payment_id = payload.get("payment_id")
        payment_status = payload.get("payment_status")
        order_id = payload.get("order_id")

        if payment_status.lower() != "confirmed":
            return JsonResponse({"message": "Payment not confirmed yet."}, status=200)

        payment = Payment.objects.get(order_id=order_id)

        if payment.status == "Paid":
            return JsonResponse({"message": "Already processed."}, status=200)

        # Update subscription now
        user = payment.user
        plan = payment.plan

        subscription, _ = UserSubscription.objects.get_or_create(user=user)
        new_limit = plan.character_limit
        remaining_balance = max(subscription.balance, 0)
        new_balance = remaining_balance + new_limit

        subscription.plan = plan
        subscription.promo = 1 if plan.name.lower() == "free" else subscription.promo
        subscription.characters_used = 0
        subscription.limit = new_limit
        subscription.balance = new_balance
        subscription.ip_address = get_client_ip(request)
        subscription.start_date = timezone.now()
        subscription.save()

        # Mark payment as paid
        payment.status = 'Paid'
        payment.save()

        return JsonResponse({"message": "Subscription updated successfully."}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# @login_required
# def subscribe_user(request, plan_name):
#     user = request.user
#     plan = get_object_or_404(SubscriptionPlan, name__iexact=plan_name)
#     ip = get_client_ip(request)

#     try:
#         subscription, created = UserSubscription.objects.get_or_create(user=user)

#         # Calculate new balance by adding existing unused balance to new plan limit
#         remaining_balance = subscription.balance if subscription.balance > 0 else 0
#         new_limit = plan.character_limit
#         new_balance = remaining_balance + new_limit

#         subscription.plan = plan
#         subscription.promo = 1
#         subscription.characters_used = 0  # Optional: reset or keep it as log
#         subscription.limit = new_limit
#         subscription.balance = new_balance
#         subscription.ip_address = ip
#         subscription.start_date = timezone.now().date()
#         subscription.save()

#         messages.success(request, f"You're now subscribed to {plan.name}!")
#     except Exception as e:
#         messages.error(request, f"Subscription failed: {e}")
#         return redirect('subscription_page')

#     # Load TTS voices
#     voices = []
#     try:
#         voices = async_to_sync(edge_tts.list_voices)()
#     except Exception as e:
#         messages.warning(request, "Failed to load voices.")

#     return render(request, 'tts/index.html', {'voices': voices})



# @login_required
# def subscribe_user(request, plan_name):
#     user = request.user
#     plan = get_object_or_404(SubscriptionPlan, name__iexact=plan_name)
#     ip = get_client_ip(request)

#     try:
#         UserSubscription.objects.update_or_create(
#             user=user,
#             defaults={
#                 'characters_used': 0,
#                 'plan': plan,
#                 'ip_address': ip,
#                 'start_date': timezone.now().date(),
#             }
#         )
#         messages.success(request, f"You're now subscribed to {plan.name}!")
#     except Exception as e:
#         messages.error(request, f"Subscription failed: {e}")
#         return redirect('subscription_page')  # Update with your actual URL name

#     # Load TTS voices
#     voices = []
#     try:
#         voices = async_to_sync(edge_tts.list_voices)()
#     except Exception as e:
#         messages.warning(request, "Failed to load voices.")

#     return render(request, 'tts/index.html', {'voices': voices})







# @login_required
# def subscribe_user(request, plan_name):
#     user = request.user
#     plan = get_object_or_404(SubscriptionPlan, name__iexact=plan_name)
#     ip = get_client_ip(request)

#     # Update or create subscription
#     try:
#         UserSubscription.objects.update_or_create(
#             user=user,
#             defaults={
#                 'subscription': plan,
#                 'ip_address': ip,
#             }
#         )
#         messages.success(request, f"Successfully subscribed to {plan.name}!")
#     except Exception as e:
#         messages.error(request, f"Subscription update failed: {str(e)}")
#         return redirect('subscription_page')  # replace with your actual subscription page URL name

#     # Load voices
#     voices = []
#     try:
#         voices = async_to_sync(edge_tts.list_voices)()
#     except Exception as e:
#         messages.warning(request, "Could not load voice options. Please try again later.")

#     context = {
#         'voices': voices
#     }

#     return render(request, 'tts/index.html', context)


def subscribe(request):
    subs = SubscriptionPlan.objects.all()
    context = {
        'subs': subs
    }
    return render(request, 'tts/subscribe.html', context)

def banktransfer(request, name):
    plan = get_object_or_404(SubscriptionPlan, name__iexact=name)

    context = {
        'plan': plan
    }
    return render(request, 'tts/banktransfer.html', context)


def register(request):
    return render(request, 'tts/register.html')

@csrf_exempt 
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        username = slugify(username)

        # Check if passwords match
        if password != password_confirm:
            return JsonResponse({'message': 'Password Do Not Match'}, status=400)

        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'message': 'Username already taken.'}, status=400)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'message': 'Email already taken.'}, status=400)

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        return JsonResponse({'message': 'registered', 'user': user.username})

    return JsonResponse({'message': 'Invalid request'}, status=400)



# CSRF protection is not exempt in this case
@csrf_protect
def login_view(request):
    if request.method == "POST":
        # Use request.POST.get() for POST data
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if user exists and password is correct
        user = User.objects.filter(username=username).first()
        
        if user is not None and user.check_password(password):
            # Log the user in
            login(request, user)
            return JsonResponse({'message': 'Login successful!', 'user': user.username})
        
        # Return error message if username or password is invalid
        return JsonResponse({'message': 'Invalid username or password'}, status=400)
    
    # If GET request, render the login page (for form submission)
    return render(request, 'tts/login.html')

def logout_view(request):
    logout(request)  # Logs out the user
    # return JsonResponse({'message': 'Logged out successfully'})
    return redirect('tts')
