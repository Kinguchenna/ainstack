from django.db import models

# Create your models here.

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    content = models.TextField(blank=True)  # extracted text
    uploaded_at = models.DateTimeField(auto_now_add=True)