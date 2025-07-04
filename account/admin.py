from django.contrib import admin
from account.models import UserSubscription, SubscriptionPlan, DownloadHistory, Payment, EmailVerification
# Register your models here.

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_verified')
    search_fields = ('user', 'token')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'characters_used', 'ip_address', 'start_date','balance','limit','promo')
    search_fields = ('user__username', 'plan__name')

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'character_limit', 'price')
    search_fields = ('name',)


@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ('video_url', 'user', 'email')
    search_fields = ('user',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'payment_id','token_id','order_description','price_amount','status')
    search_fields = ('user',)