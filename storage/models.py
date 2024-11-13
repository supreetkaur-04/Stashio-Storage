# storage/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django import forms

# List of allowed file extensions
ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx']

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    size = models.IntegerField(null=False)  # Store the size of the file
    uploaded_at = models.DateTimeField(auto_now_add=True)
    folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # If no size provided, set it to the file's size
        if not self.size and self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.file.delete(save=False)  # Delete file from storage when the object is deleted
        super().delete(*args, **kwargs)

# Function to calculate the total storage used by a user
def get_user_storage_usage(user):
    # Calculate total file size for the given user
    total_storage = File.objects.filter(user=user).aggregate(Sum('size'))['size__sum'] or 0
    return total_storage


# Folder Model
class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.parent == self:
            raise ValidationError("A folder cannot be its own parent.")

    def __str__(self):
        return self.name
