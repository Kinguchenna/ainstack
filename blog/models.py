from django.db import models

class Blog(models.Model):
    CATEGORY_CHOICES = [
        ('Inspiration', 'Inspiration'),
        ('Tech', 'Tech'),
        ('Health', 'Health'),
        # Add more as needed
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='blog_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
