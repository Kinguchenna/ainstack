# myapp/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerification  # Your custom model
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_verification_and_send_email(sender, instance, created, **kwargs):
    if created:
        verification = EmailVerification.objects.create(user=instance)
        verification_link = f"http://yourdomain.com/verify-email/{verification.token}/"

        subject = 'Verify Your Email Address'
        message = f"Hi {instance.username},\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nThis link will expire in 24 hours."
        recipient_list = [instance.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
