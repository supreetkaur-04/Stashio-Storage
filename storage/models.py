# storage/models.py

from django.db import models
from django.contrib.auth.models import User 
from django.db.models import Sum

# Folder model for cloud storage
class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)  

    def __str__(self):
        return self.name

# File model for uploaded files
class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # Fix: Move this inside the class
    def save(self, *args, **kwargs):
        if not self.size and self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)

def get_user_storage_usage(user):
    return File.objects.filter(user=user).aggregate(Sum('size'))['size__sum'] or 0


