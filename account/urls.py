from django.urls import path
from .views import register_view, login_view, logout_view, register, subscribe, subscribe_user, payment_webhook,banktransfer
from .views import subscribe_free
urlpatterns = [
    path('subscribe-user/<str:plan_name>/', subscribe_user, name='subscribe_user'),
    path('subscribe/', subscribe, name='subscribe'),
    path('subscribe-free/<str:plan_name>/', subscribe_free, name='subscribe_free'),
    path('banktransfer/<str:name>', banktransfer, name='banktransfer'),
    
    path('register/', register, name='register'),
    path('register-view/', register_view, name='register_view'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('payment/webhook/', payment_webhook, name='payment_webhook'),
]
