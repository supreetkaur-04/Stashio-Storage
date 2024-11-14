# storage/views.py

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.http import FileResponse
from .forms import FolderForm, FileUploadForm, SignupForm, SubfolderForm
from .models import Folder, File, get_user_storage_usage
from django.db.models import Sum


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created successfully!')
            return redirect('storage:file_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'storage:file_list')  # Redirecting to file list after login
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('storage:login')  # Redirecting to login page after logout


@login_required
def upload_file(request):
    storage_limit = 100 * 1024 * 1024  # 100MB limit
    storage_used = get_user_storage_usage(request.user)
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file_size = request.FILES['file'].size
            if storage_used + new_file_size > storage_limit:
                messages.error(request, 'You cannot upload this file because it exceeds your storage limit.')
                return redirect('storage:file_list')  # Redirecting to file list if over storage limit
            file = form.save(commit=False)
            file.user = request.user
            file.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('storage:file_list')  # Redirecting to file list after upload
    else:
        form = FileUploadForm()
    
    return render(request, 'upload_file.html', {'form': form})


def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    
    # Check if the file belongs to the logged-in user
    if file.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this file.")
    
    try:
        file.delete()
        messages.success(request, 'File deleted successfully!')
    except Exception as e:
        messages.error(request, f"Error deleting file: {e}")
    
    return redirect('storage:file_list')  # Redirecting to file list after delete


def file_download(request, file_id):
    file = get_object_or_404(File, id=file_id)
    
    # Ensure the file belongs to the current user
    if file.user != request.user:
        return HttpResponseForbidden("You are not authorized to access this file.")
    
    try:
        return FileResponse(file.file, as_attachment=True)
    except FileNotFoundError:
        messages.error(request, "The requested file could not be found.")
        return redirect('storage:file_list')


@login_required
def file_list(request):
    query = request.GET.get('q', '')

    # Get files and folders for the logged-in user
    files = File.objects.filter(user=request.user, name__icontains=query)
    folders = Folder.objects.filter(user=request.user, name__icontains=query)

    storage_used = get_user_storage_usage(request.user)
    storage_limit = 100 * 1024 * 1024  # Example: 100MB storage limit
    storage_remaining = storage_limit - storage_used

    return render(request, 'file_list.html', {
        'files': files,
        'folders': folders,
        'query': query,
        'storage_used': storage_used,
        'storage_remaining': storage_remaining
    })


@login_required
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('name')
        if folder_name:
            folder = Folder(name=folder_name, user=request.user)  # Add any additional fields you need
            folder.save()
            messages.success(request, f"Folder '{folder_name}' created successfully!")
            return redirect('storage:folder_detail', folder_id=folder.id)
        else:
            messages.error(request, "Folder name cannot be empty.")
    return render(request, 'folder_create.html')  # This template should contain the form for creating a folder


def folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    files = File.objects.filter(folder=folder)
    return render(request, 'folder_view.html', {'folder': folder, 'files': files})


def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)

    # Optional: Check if the folder has any files/subfolders
    if folder.files.count() > 0 or folder.subfolders.count() > 0:
        messages.error(request, "Cannot delete folder because it is not empty.")
        return redirect('storage:folder_view', folder_id=folder.id)
    
    # Delete the folder
    folder.delete()
    messages.success(request, f"Folder '{folder.name}' has been deleted successfully.")
    return redirect('storage:file_list')


def add_file_to_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.folder = folder  # Set the folder for the uploaded file
            file.save()
            messages.success(request, "File uploaded successfully!")
            return redirect('storage:folder_view', folder_id=folder.id)
    else:
        form = FileUploadForm()
    
    return render(request, 'storage/add_file_to_folder.html', {'form': form, 'folder': folder})


@login_required
def create_subfolder(request, folder_id):
    parent_folder = get_object_or_404(Folder, id=folder_id, user=request.user)

    if request.method == 'POST':
        subfolder_name = request.POST.get('name')
        if subfolder_name:
            subfolder = Folder(name=subfolder_name, parent=parent_folder, user=request.user)
            subfolder.save()
            messages.success(request, f"Subfolder '{subfolder_name}' created successfully!")
            return redirect('storage:folder_detail', folder_id=parent_folder.id)
        else:
            messages.error(request, "Subfolder name cannot be empty.")
    
    return render(request, 'create_subfolder.html', {'parent_folder': parent_folder})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')  # Redirect to login page after successful signup
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def folder_detail(request, folder_id):
    # Get the folder or return a 404 if not found
    folder = get_object_or_404(Folder, id=folder_id)

    # Retrieve subfolders within this folder (assuming 'parent' is a foreign key to Folder)
    subfolders = Folder.objects.filter(parent=folder)  # Assuming you have a 'parent' field in Folder
    
    # Retrieve files associated with this folder
    files = File.objects.filter(folder=folder)  # Assuming 'folder' is a foreign key in File
    
    # Count the number of files and subfolders
    num_files = files.count()
    num_subfolders = subfolders.count()
    
    # Optional: Check if the user has permission to view this folder (if not public)
    if not folder.is_public and not request.user.has_perm('view_folder', folder):
        return render(request, 'permission_denied.html', {'folder': folder})

    # Pass the folder, its subfolders, and files to the template
    return render(
        request,
        'folder_detail.html',
        {
            'folder': folder,
            'subfolders': subfolders,
            'files': files,
            'num_files': num_files,
            'num_subfolders': num_subfolders,
        }
    )
