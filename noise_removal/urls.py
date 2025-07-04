from django.urls import path
from  .views import upload_audio, noice_result,post_upload_audio
from django.conf import settings
from django.conf.urls.static import static

app_name = 'noise_removal'  # THIS is critical

urlpatterns = [
    path('noise-removal/', upload_audio, name='upload_audio'),
    path('noise-result/<str:filename>/', noice_result, name='noice_result'),
    path('post-upload-audio/', post_upload_audio, name='post_upload_audio'),
    
]



if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)