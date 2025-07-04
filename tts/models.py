from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class CustomVoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voice_name = models.CharField(max_length=100)
    voice_file = models.FileField(upload_to='voices/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.voice_name}"
