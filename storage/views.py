from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseForbidden
from django.http import FileResponse
from .forms import FolderForm, FileUploadForm
from .models import Folder, File, get_user_storage_usage
from django.views.generic import ListView
from .models import File
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib.auth.models import User

def home(request):
    return render(request, 'home.html') 

def home_view(request):
    return render(request, 'home.html')  # Or whatever template you're using

# Registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('file_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('file_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.user = request.user  # Associate with user
            file.save()
            return redirect('file_list')
    else:
        form = FileUploadForm()
    return render(request, 'upload_file.html', {'form': form})


# Folder view (to display files in a folder)
def folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)  # Ensure user owns the folder
    files = File.objects.filter(folder=folder)
    return render(request, 'folder_view.html', {'folder': folder, 'files': files})

def file_download(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if file.user != request.user:
        return HttpResponseForbidden("You are not authorized to access this file.")
    
    # Serve the file using FileResponse
    return FileResponse(file.file)

# Create folder view
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST, user=request.user)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user  # Assign the folder to the current user
            folder.save()
            return redirect('folder_list')
    else:
        form = FolderForm()
    return render(request, 'create_folder.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# Delete file view
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if file.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this file.")
    file.delete()
    return redirect('file_list')

# List of files (with search query and user-specific filter)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Decorator to ensure the user is logged in
@login_required
def file_list(request):
    query = request.GET.get('q', '')
    if request.user.is_authenticated:
        files = File.objects.filter(user=request.user, name__icontains=query)
    else:
        return redirect('login') 
    return render(request, 'file_list.html', {'files': files, 'query': query})

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Create the user
            user = User.objects.create_user(username=username, password=password)
            login(request, user)  # Log the user in after signup
            
            return redirect('file_list')  # Redirect to a page after successful signup
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def signup_view(request):
    return render(request, 'signup.html') 

def logged_out_view(request):
    # Optionally, log out the user if you haven't already done so
    logout(request)
    
    # Render the logged-out page (could be a template with a message)
    return render(request, 'logged_out.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')  # Redirect to login page after successful signup
        else:
            messages.error(request, 'There was an error with your signup. Please try again.')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

class FileListView(ListView):
    model = File
    template_name = 'file_list.html'  # Specify the template you want to render
    context_object_name = 'files'