# storage/views.py

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, FileResponse         # (this file response)
from .forms import FileUploadForm, FolderCreateForm, CustomUserCreationForm
from .models import Folder, File, get_user_storage_usage, get_user_storage_info,  MAX_STORAGE_LIMIT
from .forms import CustomLoginForm
from django.conf import settings


@login_required
def dashboard(request):
    storage_info = get_user_storage_info(request.user)
    return render(request, 'dashboard.html', {'storage': storage_info})

def home(request):
    return render(request, 'home.html')

# def login_view(request):
#     if request.method == 'POST':
#         form = UsernameOrEmailLoginForm(request, data=request.POST)
#         if form.is_valid():
#             login(request, form.get_user())
#             return redirect('storage:file_list')
#     else:
#         form = UsernameOrEmailLoginForm()
#     return render(request, 'login.html', {'form': form})

# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Your account has been created successfully!')
#             return redirect('storage:home') 
#     else:
#         form = UserCreationForm()
#     return render(request, 'signup.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.save()
            login(request, user)
            messages.success(request, 'Your account has been created successfully!')
            return redirect('storage:home')
    else:
        base_username = request.GET.get("base_username", "user")
        form = CustomUserCreationForm()
        form.fields["username"].initial = CustomUserCreationForm().suggest_unique_username(base_username)
    return render(request, 'signup.html', {'form': form})
 

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.user 
            login(request, user)
            next_url = request.GET.get('next', 'storage:file_list') 
            return redirect(next_url)
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('storage:login')  


# @login_required
# def upload_file(request, folder_id=None):
#     if folder_id:
#         folder = get_object_or_404(Folder, id=folder_id, user=request.user)
#     else:
#         folder = None  
#     if request.method == 'POST':
#         form = FileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = form.save(commit=False)
#             file.user = request.user
#             if folder:
#                 file.folder = folder 
#             file.save()
#             messages.success(request, "File uploaded successfully!")
#             if folder:
#                 return redirect('storage:folder_detail', folder_id=folder.id)
#             else:
#                 return redirect('storage:file_list') 
#         else:
#             messages.error(request, "Error uploading the file.")
#     else:
#         form = FileUploadForm()
#     return render(request, 'upload_file.html', {'folder': folder, 'form': form})

@login_required
def upload_file(request, folder_id=None):
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    else:
        folder = None

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Get total used storage by this user
            user_files = File.objects.filter(user=request.user)
            used_storage = sum(f.file.size for f in user_files)
            
            if used_storage + uploaded_file.size > settings.MAX_STORAGE_LIMIT:
                messages.error(request, "❌ Storage limit exceeded. Cannot upload this file.")
                return redirect('storage:file_list')  # or reload the form page
            
            # Save the file if within limit
            file = form.save(commit=False)
            file.user = request.user
            if folder:
                file.folder = folder
            file.save()
            messages.success(request, "✅ File uploaded successfully!")
            if folder:
                return redirect('storage:folder_detail', folder_id=folder.id)
            else:
                return redirect('storage:file_list')
        else:
            messages.error(request, "❌ Error uploading the file.")
    else:
        form = FileUploadForm()
        
    return render(request, 'upload_file.html', {'folder': folder, 'form': form})


def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    if file.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this file.")
    try:
        file.delete()
        messages.success(request, 'File deleted successfully!')
    except Exception as e:
        messages.error(request, f"Error deleting file: {e}")
    return redirect('storage:file_list') 


def file_download(request, file_id):
    try:
        file = File.objects.get(id=file_id, user=request.user)
        return FileResponse(file.file, as_attachment=True)
    except File.DoesNotExist:
        messages.error(request, "File not found.")
        return redirect('storage:file_list')
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('storage:file_list')


# @login_required
# def file_list(request):
#     query = request.GET.get('q', '')
#     files = File.objects.filter(user=request.user, folder__isnull=True, name__icontains=query)  
#     folders = Folder.objects.filter(user=request.user, parent__isnull=True, name__icontains=query)  
#     storage_used = get_user_storage_usage(request.user)
#     storage_limit = 100 * 1024 * 1024  
#     storage_remaining = storage_limit - storage_used
#     return render(request, 'file_list.html', {
#         'files': files,
#         'folders': folders,
#         'query': query,
#         'storage_used': storage_used,
#         'storage_remaining': storage_remaining
#     })

@login_required
def file_list(request):
    # 1. Fetch files & folders
    files = File.objects.filter(user=request.user, folder__isnull=True)
    folders = Folder.objects.filter(user=request.user, parent__isnull=True)

    # 2. Get all storage info at once
    storage = get_user_storage_info(request.user)

    context = {
        'files': files,
        'folders': folders,
        'storage': storage,
        'MAX_STORAGE': MAX_STORAGE_LIMIT,
    }
    return render(request, 'file_list.html', context)

@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderCreateForm(request.POST) 
        if form.is_valid():
            folder_name = form.cleaned_data['folder_name']
            folder = Folder(name=folder_name, user=request.user)
            folder.save()
            messages.success(request, f"Folder '{folder_name}' created successfully!")
            return redirect('storage:folder_detail', folder_id=folder.id)      
        else:
            messages.error(request, "Error creating folder.")
    else:
        form = FolderCreateForm() 
    return render(request, 'folder_create.html', {'form': form})


def folder_view(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    files = File.objects.filter(folder=folder)
    subfolders = Folder.objects.filter(parent=folder)
    return render(request, 'folder_view.html', {'folder': folder, 'files': files, 'subfolders': subfolders})


def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if folder.files.count() > 0 or folder.subfolders.count() > 0:
        messages.error(request, "Cannot delete folder because it is not empty.")
        return redirect('storage:folder_view', folder_id=folder.id)
    folder.delete()
    messages.success(request, f"Folder '{folder.name}' has been deleted successfully.")
    return redirect('storage:file_list')


def upload_file_with_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.folder = folder
            uploaded_file.save()
            return redirect('folder_detail', folder_id=folder.id)
    else:
        form = FileUploadForm()
    return render(request, 'upload_file.html', {
        'folder': folder,
        'form': form
    })


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


@login_required
def folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    files = File.objects.filter(folder=folder)
    subfolders = Folder.objects.filter(parent=folder)
    if request.method == 'POST' and 'upload_file' in request.POST:
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.folder = folder  
            new_file.user = request.user  
            new_file.save()
            messages.success(request, f"File '{new_file.name}' uploaded successfully!")
            return redirect('storage:folder_detail', folder_id=folder.id)
        else:
            messages.error(request, f"Error uploading file: {form.errors}")
    else:
        form = FileUploadForm()
    return render(request, 'folder_detail.html', {
        'folder': folder,
        'files': files,
        'form': form,
        'subfolders': subfolders,
    })


@login_required
def folder_list(request):
    folders = Folder.objects.filter(user=request.user)
    storage_used = float(get_user_storage_usage(request.user))
    storage_limit = 100 * 1024 * 1024  # 100MB in bytes
    storage_percent = min((storage_used / storage_limit) * 100, 100)
    files = File.objects.filter(user=request.user)

    return render(request, 'file_list.html', {
        'files': files,
        'folders': folders,
        'storage_used': storage_used,
        'storage_percent': storage_percent,
        'MAX_STORAGE': storage_limit
    })
    