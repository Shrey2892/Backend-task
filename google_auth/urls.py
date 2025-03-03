from django.urls import path
from .views import google_login, google_callback,logout_view,get_google_user_info,google_logout,list_google_drive_files,get_all_users
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', google_login, name='google_login'),
    path('callback/', google_callback, name='google_callback'),
    path('login-success',TemplateView.as_view(template_name="success.html"),name="login_success"),
    path('user-info/',get_google_user_info,name="user-info"),
    path('google/drive/files',list_google_drive_files,name="drive-files"),
    path('logout/',logout_view,name="logout"),
    path('google_logout',google_logout,name="google_logout"),
    path('users/',get_all_users,name="users"),

]
