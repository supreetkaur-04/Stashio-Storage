# storage/urls.py

from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home_view, name='home'),
    path('register/', views.register, name='register'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logged_out/', views.logged_out_view, name='logged_out'),
    path('files/', views.file_list, name='file_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/<int:file_id>/download/', views.file_download, name='file_download'),
    path('folders/<int:folder_id>/', views.folder_view, name='folder_view'),
    path('folders/create/', views.create_folder, name='create_folder'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
]

