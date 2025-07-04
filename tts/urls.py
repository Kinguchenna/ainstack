from django.urls import path
from .views import upload_voice, tts, process_voice, supported_voices, texttosong, process_song, start_checkout, payment_complete, text_to_speach
from .views import translate_text, sample_voice, load_sample_voice,preferences_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', tts, name='tts'),
    path('tts/', process_voice, name='process_voice'),
    path('preferences_view/', preferences_view, name='preferences_view'),
    path('sample-voice/', sample_voice, name='sample_voice'),
    path('load-sample-voice/', load_sample_voice, name='load_sample_voice'),
    path('text-to-speach/', text_to_speach, name='text_to_speach'),
    path('supported_voices/', supported_voices, name='supported_voices'),
    path('texttosong/', texttosong, name='texttosong'),
    path('process_song/', process_song, name='process_song'),
    path('checkout/<int:plan_id>/', start_checkout, name='checkout'),
    path('payment-complete/', payment_complete, name='payment_complete'),
    path('translate-text', translate_text, name='translate_text'),
    path('upload-voice/', upload_voice, name='upload_voice'),
]



if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)