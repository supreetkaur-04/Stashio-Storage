# storage/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.file_list, name='file_list'),
    path('files/<int:file_id>/download/', views.file_download, name='file_download'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('folder/create/', views.create_folder, name='create_folder'),
    path('folder/<int:folder_id>/', views.folder_view, name='folder_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
