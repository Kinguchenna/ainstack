from django.urls import path
from .views import audio2text, transcribe_audio

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('audio-to-text/', audio2text, name='audio2text'),
    path('transcribe-audio/', transcribe_audio, name='transcribe_audio'),
]



if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)