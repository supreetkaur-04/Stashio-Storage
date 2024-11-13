# storage/forms.py

from django import forms
from .models import File, Folder, ALLOWED_EXTENSIONS
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# Form to upload a file
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']

    # Add file validation for size and type
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


# Form for user signup using Django's built-in UserCreationForm
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


# Form to create/edit folders
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user')
        super().__init__(*args, **kwargs)
        if user:
            # Limit the parent folder options to folders owned by the same user
            self.fields['parent'].queryset = Folder.objects.filter(user=user)

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if parent == self.instance:
            raise forms.ValidationError("A folder cannot be its own parent.")
        return parent
