from django.urls import path
from .views import process_youdownload, youdownload, delete_file, get_download_progress

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('process-youtube', process_youdownload, name='process_youdownload'),
    path('youtube/', youdownload, name='youdownload'),
    path('delete-file/', delete_file, name='delete_file'),
    path('get-download-progress/', get_download_progress, name='get_download_progress'),
    
]

if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)