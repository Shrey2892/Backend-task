from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('google_auth.urls')),
    path('drive/', include('drive.urls')),
    path('chat/', include('chat.urls')),
]
