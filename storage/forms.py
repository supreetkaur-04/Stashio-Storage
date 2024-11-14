# storage/forms.py

from django import forms
from .models import File, Folder, ALLOWED_EXTENSIONS
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx']

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']  # Fields for file upload

    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        # Max file size (10 MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise forms.ValidationError("File size exceeds the 10MB limit.")
        
        # Check file extension
        file_extension = file.name.split('.')[-1].lower()  # Get the file extension (in lowercase)
        if file_extension not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(f"Invalid file type. Allowed extensions are: {', '.join(ALLOWED_EXTENSIONS)}.")
        
        return file


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']  # Parent folder selection

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Limit the parent folder options to folders owned by the same user
            self.fields['parent'].queryset = Folder.objects.filter(user=user)

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent == self.instance:
            raise forms.ValidationError("A folder cannot be its own parent.")
        return parent

class FolderCreateForm(forms.Form):
    folder_name = forms.CharField(max_length=100, required=True, label='Folder Name') 

class SubfolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name'] 