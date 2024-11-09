# storage/forms.py

from django import forms
from .models import File, Folder

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']
    
    # Add file size validation
    def clean_file(self):
        file = self.cleaned_data.get('file')
        max_size = 10 * 1024 * 1024  # 10 MB limit
        if file.size > max_size:
            raise forms.ValidationError("File size exceeds the 10MB limit.")
        return file

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user')
        super().__init__(*args, **kwargs)
        if user:
            self.fields['parent'].queryset = Folder.objects.filter(user=user)

