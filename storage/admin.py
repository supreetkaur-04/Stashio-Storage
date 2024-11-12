# storage/admin.py

from django.contrib import admin
from .models import File, Folder

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'size', 'uploaded_at', 'user', 'folder')

    def save_model(self, request, obj, form, change):
        print("Saving file:", obj.name)
        super().save_model(request, obj, form, change)

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'parent')