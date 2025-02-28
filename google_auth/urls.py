from django.urls import path
from .views import google_login, google_callback,logout_view
from django.views.generic import TemplateView

urlpatterns = [
    path('login/', google_login, name='google_login'),
    path('callback/', google_callback, name='google_callback'),
    path('login-success',TemplateView.as_view(template_name="success.html"),name="login_success"),
    path('logout/',logout_view,name="logout"),
]
