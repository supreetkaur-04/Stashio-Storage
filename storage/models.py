# storage/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .utils import validate_file

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx']

class File(models.Model):
    # name = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True) 
    file = models.FileField(upload_to='files/')
    size = models.BigIntegerField(null=False) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.size and self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def clean(self):
        validate_file(self.file)


def get_user_storage_usage(user):
    total_storage = File.objects.filter(user=user).aggregate(Sum('size'))['size__sum'] or 0
    return total_storage

from django.db.models import Sum

def get_user_storage_info(user):
    total_used = File.objects.filter(user=user).aggregate(Sum('size'))['size__sum'] or 0
    max_limit = 10 * 1024 * 1024 * 1024  # 10 GB
    remaining = max_limit - total_used
    percent_used = round((total_used / max_limit) * 100, 2) if max_limit else 0
    return {
        'used': total_used,
        'remaining': max(0, remaining),
        'percent': min(100, percent_used),
        'max': max_limit
    }


MAX_STORAGE_LIMIT = 10 *1024 * 1024 * 1024 


class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.parent and self.parent.id == self.id:
            raise ValidationError("A folder cannot be its own parent.")

    def __str__(self):
        return self.name

    @property
    def subfolders(self):
        return Folder.objects.filter(parent=self)

    @property
    def files(self):
        return File.objects.filter(folder=self)

