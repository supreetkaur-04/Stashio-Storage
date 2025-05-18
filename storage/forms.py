# storage/forms.py

from django import forms
from .models import File, Folder, ALLOWED_EXTENSIONS
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from allauth.account.forms import LoginForm
from django.contrib.auth.forms import AuthenticationForm
import uuid


ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'txt', 'doc', 'docx', 'xls', 'xlsx']

class UsernameOrEmailLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={"placeholder": "username or email"})
    )

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = "Username or Email"
        self.fields['login'].widget = forms.TextInput(
            attrs={"placeholder": "Enter username or email"}
        )


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
        fields = ['name','file'] #('file',) 
    name = forms.CharField(max_length=100, label="File Name")
    file = forms.FileField(label="Select File")

    def clean_file(self):
        file = self.cleaned_data.get('file')
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise forms.ValidationError("File size exceeds the 10MB limit.")
        file_extension = file.name.split('.')[-1].lower()  # Get the file extension (in lowercase)
        if file_extension not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(f"Invalid file type. Allowed extensions are: {', '.join(ALLOWED_EXTENSIONS)}.")
        return file

# storage/forms.py

# from django import forms
# from .models import File
# from django.conf import settings

# ALLOWED_EXTENSIONS = getattr(settings, 'ALLOWED_EXTENSIONS', [])

# class FileUploadForm(forms.ModelForm):
#     class Meta:
#         model = File
#         fields = ('file',)    # ← no ‘name’ here

#     file = forms.FileField(label="Select File")

#     def clean_file(self):
#         f = self.cleaned_data['file']
#         if f.size > 10*1024*1024:
#             raise forms.ValidationError("Max size 10MB.")
#         ext = f.name.rsplit('.', 1)[-1].lower()
#         if ext not in ALLOWED_EXTENSIONS:
#             raise forms.ValidationError(
#                 f"Only {', '.join(ALLOWED_EXTENSIONS)} files allowed."
#             )
#         return f

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         # grab the original filename from the uploaded file object:
#         instance.name = self.cleaned_data['file'].name
#         if commit:
#             instance.save()
#         return instance


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']  

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
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


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def suggest_unique_username(self, base_username):
        """
        Suggest a unique username by appending a random UUID if the base username exists.
        """
        if not User.objects.filter(username=base_username).exists():
            return base_username
        while True:
            unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"
            if not User.objects.filter(username=unique_username).exists():
                return unique_username
