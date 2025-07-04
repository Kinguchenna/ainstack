from django.urls import path
from  .views import apiDocumentation, aboutus, careers, captcha_view,logout_human,show_logs
from django.conf import settings
from django.conf.urls.static import static

app_name = 'general'  # THIS is critical

urlpatterns = [
    path('captcha/', captcha_view, name='captcha'),
    path('api-documentation', apiDocumentation, name="apiDocumentation"),
    path('about-us', aboutus, name="aboutus"),
    path('careers', careers, name="careers"),
    path('logout-human/', logout_human, name='logout_human'),
    path('logs/', show_logs, name='show_logs'),
]



if settings.DEBUG:  # This should only be True in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)