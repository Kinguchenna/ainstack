# urls.py in app
from django.urls import path
from . import views

urlpatterns = [
    path('text-extractor/', views.upload_document, name='upload'),
    path('search/', views.search_documents, name='search'),
]
