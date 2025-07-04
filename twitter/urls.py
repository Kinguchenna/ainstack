from django.urls import path
from .views import twitter, index, get_twitter_progress

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('twitter', twitter, name='twitter'),
    path('twit', index, name='index'),
    path('get-twitter-progress/', get_twitter_progress, name='get_twitter_progress'),
    
    
]

if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)