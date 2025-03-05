from django.urls import path
from . import views

urlpatterns = [
    path("files/", views.list_google_drive_files, name="list_google_drive_files"),
    path("download/<str:file_id>/", views.download_google_drive_file, name="download_google_drive_file"),
    path("delete/<str:file_id>/", views.delete_google_drive_file, name="delete_google_drive_file"),
    path("upload/", views.upload_to_google_drive, name="upload_to_google_drive"),
]
