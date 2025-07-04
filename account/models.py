from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import uuid

# Create your models here.


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(days=1)  # Link valid for 1 day

    def __str__(self):
        return f"{self.user.username} - Verified: {self.is_verified}"

class DownloadHistory(models.Model):
    video_url = models.URLField()
    file = models.URLField(default=" ")    
    downloaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="name")
    email = models.CharField(max_length=100, default="email")

    def __str__(self):
        return self.video_url
    

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    character_limit = models.PositiveIntegerField()
    download_limit = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    duration_days = models.PositiveIntegerField(default=30)  # 30-day subscriptions

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    characters_used = models.PositiveIntegerField(default=0)
    download_used = models.PositiveIntegerField(default=0)
    balance = models.PositiveIntegerField(default=0)
    limit = models.PositiveIntegerField(default=0)
    promo = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)


    @classmethod
    def check_suspicious_activity(cls, ip_address):
        user_count = cls.objects.filter(ip_address=ip_address).count()
        if user_count > 1:
            return "Suspicious activity detected"
        return "No suspicious activity"

    def is_active(self):
        from django.utils import timezone
        return timezone.now() < self.start_date + timezone.timedelta(days=self.plan.duration_days)

    def remaining_characters(self):
        if self.plan is None:
            return 0  # Or raise an exception, or return a default limit
        # return max(0, (self.plan.character_limit + self.balance) - self.characters_used)
        print("this is your self balance", self.balance)
        return max(0, self.balance)

    # def __str__(self):
    #     return f"{self.user.username} - {self.plan.name}"
    def __str__(self):
        user = self.user.username if self.user else "Unknown User"
        plan = self.plan.name if self.plan else "No Plan"
        return f"{user} - {plan}"
    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, null=True, blank=True, on_delete=models.SET_NULL)

# Connect signal to auto-create profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    
    payment_id = models.CharField(max_length=100)  # 'id' from API
    token_id = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.CharField(max_length=100)
    order_description = models.TextField()
    
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency = models.CharField(max_length=10)
    pay_currency = models.CharField(max_length=10, null=True, blank=True)
    
    invoice_url = models.URLField()
    success_url = models.URLField()
    cancel_url = models.URLField()
    
    ipn_callback_url = models.URLField(null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    
    partially_paid_url = models.URLField(null=True, blank=True)
    payout_currency = models.CharField(max_length=10, null=True, blank=True)
    
    is_fixed_rate = models.BooleanField(default=False)
    is_fee_paid_by_user = models.BooleanField(default=False)
    source = models.CharField(max_length=100, null=True, blank=True)
    collect_user_data = models.BooleanField(default=False)
    
    status = models.CharField(max_length=50, default='Pending')  # 'Pending', 'Paid', 'Failed', etc.
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.order_id}"
    



class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_voice = models.CharField(max_length=100, blank=True, null=True)
    preferred_pitch = models.CharField(max_length=10, blank=True, null=True)
    preferred_speed = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences"