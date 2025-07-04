from django.urls import path
from .views import dashboard, downloads, transfer, transfer_to, verify, verify_account, resend_verification_email
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard', dashboard, name='dashboard'),
    path('downloads', downloads, name='downloads'),
    path('transfer', transfer, name='transfer'),
    path('transfer_to', transfer_to, name='transfer_to'),
    path('verify', verify, name='verify'),
    path('verify_account', verify_account, name='verify_account'),
    path('resend_verification_email', resend_verification_email, name='resend_verification_email'),
]



if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)