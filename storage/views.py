# storage/views.py

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.http import FileResponse
from .forms import FolderForm, FileUploadForm, SignupForm
from .models import Folder, File, get_user_storage_usage


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request, user)  
            messages.success(request, 'Your account has been created successfully!')
            return redirect('file_list')  
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'file_list')  # Redirect to the page the user was trying to access
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.user = request.user  # Associate uploaded file with the user
            file.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('file_list')
    else:
        form = FileUploadForm()
    return render(request, 'upload_file.html', {'form': form})


def file_download(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if file.user != request.user:
        return HttpResponseForbidden("You are not authorized to access this file.")
    return FileResponse(file.file, as_attachment=True)


def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST, user=request.user)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user  # Associate folder with the user
            folder.save()
            messages.success(request, 'Folder created successfully!')
            return redirect('folder_list')
    else:
        form = FolderForm(user=request.user)
    return render(request, 'create_folder.html', {'form': form})


def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if file.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this file.")
    file.delete()
    messages.success(request, 'File deleted successfully!')
    return redirect('file_list')


@login_required
def file_list(request):
    query = request.GET.get('q', '')
    files = File.objects.filter(user=request.user, name__icontains=query)
    storage_used = get_user_storage_usage(request.user)
    storage_limit = 100 * 1024 * 1024  # For example, 100MB storage limit
    storage_remaining = storage_limit - storage_used
    return render(request, 'file_list.html', {'files': files, 'query': query, 'storage_used': storage_used, 'storage_remaining': storage_remaining})


def folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    files = File.objects.filter(folder=folder)
    return render(request, 'folder_view.html', {'folder': folder, 'files': files})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Optional: log the user in after sign-up
            return redirect('file_list')  # Redirect to another view after successful sign-up
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})
