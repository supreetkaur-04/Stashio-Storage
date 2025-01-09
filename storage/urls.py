# storage/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.views.decorators.http import require_GET

from . import views

app_name = 'storage'

class CustomLogoutView(LogoutView):
    @require_GET
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('upload/<int:folder_id>/', views.upload_file, name='upload_file'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.file_list, name='file_list'),
    path('files/<int:file_id>/download/', views.file_download, name='file_download'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('folder/create/', views.create_folder, name='create_folder'),
    path('folder/<int:folder_id>/', views.folder_view, name='folder_view'),
    path('folder/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    # path('folder/<int:folder_id>/add_file/', views.add_file_to_folder, name='add_file_to_folder'),
    path('folder/<int:folder_id>/upload-file/', views.upload_file_with_folder, name='upload_file_with_folder'),
    path('folder/<int:folder_id>/create-subfolder/', views.create_subfolder, name='create_subfolder'),
    path('folder/<int:folder_id>/', views.folder_detail, name='folder_detail'),
    path('folders/', views.folder_list, name='folder_list'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
