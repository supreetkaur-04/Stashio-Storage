# storage/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django import forms

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx']

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    size = models.IntegerField(null=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.SET_NULL)  # Reference 'Folder' as a string
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.size and self.file:
            self.size = self.file.size  # Automatically set the file size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.file.delete(save=False)  # Delete the file from storage
        super().delete(*args, **kwargs)
        
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        # Max file size (10 MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise forms.ValidationError("File size exceeds the 10MB limit.")
        
        # Check file extension
        file_extension = file.name.split('.')[-1].lower()  # Get the file extension (in lowercase)
        if file_extension not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("File type not allowed. Allowed types are: " + ", ".join(ALLOWED_EXTENSIONS))
        
        return file

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        if self.parent == self:
            raise ValidationError("A folder cannot be its own parent.")

    def __str__(self):
        return self.name

# Function to get user's total storage usage
def get_user_storage_usage(user):
    return File.objects.filter(user=user).aggregate(Sum('size'))['size__sum'] or 0
