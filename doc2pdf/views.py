from django.shortcuts import render, redirect
from pdf2image import convert_from_path
from .models import Document
from .forms import DocumentForm
from .utils import pdf_to_images, extract_text_from_image
from PIL import Image
import pytesseract
from blog.helper import blog_dynamic
from tts.helpers import check_internet_connectivity
from djangoML.utils import get_or_create_subscription
# Create your views here.
from django.http import JsonResponse

from account.models import UserSubscription, SubscriptionPlan


def check_network_connection():
    status = check_internet_connectivity()  # Ensure this function is defined
    return status

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For might contain multiple IPs
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# def upload_document(request):
#     # Always check network and blogs
#     network_status = check_internet_connectivity()
#     blogs = blog_dynamic()

#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)

#                     # Check network status        
#         status =  check_network_connection()
#         if not status:
#             return JsonResponse({
#                 'message': 'Please check your network and try again.'
#             }, status=403)
        
#         if form.is_valid():
#             doc = form.save()
#             text = ""
#             if doc.file.name.endswith('.pdf'):
#                 images = pdf_to_images(doc.file.path)
#                 for img in images:
#                     text += extract_text_from_image(img)
#             else:
#                 img = Image.open(doc.file.path)
#                 text = extract_text_from_image(img)

#             doc.content = text
#             doc.save()
#             return redirect('search')
#     else:
#         form = DocumentForm()

#     context = {
#         'form': form,
#         'network_status': network_status,
#         'blogs': blogs,
#     }
#     return render(request, 'doc2pdf/upload.html', context)


def upload_document(request):
    network_status = check_internet_connectivity()
    blogs = blog_dynamic()

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        status = check_internet_connectivity()  # or your wrapped sync-to-async version
        if not status:
            return JsonResponse({
                'message': 'Please check your network and try again.'
            }, status=403)
        
        user = request.user.is_authenticated
        if not user:
            return JsonResponse({
            'message': 'Please <a href="/login" style="text-decoration: none; color: #0E8AB3;background: transparent;margin: 0 0 0;padding: 2px 2px 2px;">login</a> and come back.'
             }, status=403)
        
        ip = get_client_ip(request)
        response_message =  UserSubscription.check_suspicious_activity(ip)
        if response_message == "Suspicious activity detected":
            return JsonResponse({'message': response_message}, status=403)
        

        subscription = get_or_create_subscription(request.user, char_count=200)
        if subscription is None:
            return JsonResponse({
                'message': 'Please <a href="/subscribe/" style="text-decoration: none; color: #0E8AB3;">Become a Member</a> - Downloads limit exceeded.'
            }, status=403)

        if form.is_valid():
            doc = form.save()
            text = ""

            if doc.file.name.endswith('.pdf'):
                images = pdf_to_images(doc.file.path)
                for img in images:
                    text += extract_text_from_image(img)
            else:
                img = Image.open(doc.file.path)
                text = extract_text_from_image(img)

            doc.content = text
            doc.save()

            # JSON response for AJAX success
            return JsonResponse({'status': 'success'}, status=200)

        # Form invalid
        return JsonResponse({
            'error': 'Invalid form submission.'
        }, status=400)

    else:
        form = DocumentForm()

    context = {
        'form': form,
        'network_status': network_status,
        'blogs': blogs,
    }
    return render(request, 'doc2pdf/upload.html', context)


def search_documents(request):
    # Document.objects.all().delete()
    query = request.GET.get('q')
    results = Document.objects.all()
    if query:
        results = results.filter(content__icontains=query)
    return render(request, 'doc2pdf/search.html', {'documents': results, 'query': query})

