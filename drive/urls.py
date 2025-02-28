from django.urls import path
from .views import list_drive_files

urlpatterns = [
    path('files/', list_drive_files, name='list_drive_files'),
]
