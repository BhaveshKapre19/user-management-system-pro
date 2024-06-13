# accounts/urls.py

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    HomeView, 
    ProfileView,
    ProfileEditView, 
    UserDeleteView, 
    UserFileListView, 
    UserFileCreateView,
    UserFileDetailView, 
    UserFileDeleteView,
    ShareFileView,
    AutocompleteUsersView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('profile/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('files/', UserFileListView.as_view(), name='userfile_list'),
    path('files/upload/', UserFileCreateView.as_view(), name='userfile_upload'),
    path('files/<int:pk>/', UserFileDetailView.as_view(), name='userfile_detail'),
    path('files/<int:pk>/delete/', UserFileDeleteView.as_view(), name='userfile_delete'),
    path('files/<int:file_id>/share/', ShareFileView.as_view(), name='share_file'),
    path('autocomplete-users/', AutocompleteUsersView.as_view(), name='autocomplete_users'),
]
