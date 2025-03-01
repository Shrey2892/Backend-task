import requests
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()


def get_access_token(request):
    """Retrieves and refreshes access token if expired."""
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect(reverse("google_login"))

    return access_token


def list_google_drive_files(request):
    """Fetches the user's Google Drive files using direct API requests."""
    access_token = get_access_token(request)
    if not isinstance(access_token, str):
        return access_token  # Redirect if no token

    url = "https://www.googleapis.com/drive/v3/files"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    files = response.json().get("files", [])

    return render(request, "drive_files.html", {"files": files})


def download_google_drive_file(request, file_id):
    """Downloads a file from Google Drive using direct API requests."""
    access_token = get_access_token(request)
    if not isinstance(access_token, str):
        return access_token

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        file_name = f"downloaded_{file_id}.file"
        response_obj = HttpResponse(response.content, content_type="application/octet-stream")
        response_obj["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response_obj
    
    return JsonResponse({"error": "Failed to download file"}, status=response.status_code)


def delete_google_drive_file(request, file_id):
    """Deletes a file from Google Drive using direct API requests."""
    access_token = get_access_token(request)
    if not isinstance(access_token, str):
        return access_token

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return redirect(reverse("list_google_drive_files"))
    
    return JsonResponse({"error": "Failed to delete file"}, status=response.status_code)


@csrf_exempt
def upload_to_google_drive(request):
    """Uploads a file to Google Drive using direct API requests."""
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        access_token = get_access_token(request)
        if not isinstance(access_token, str):
            return access_token

        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        headers = {"Authorization": f"Bearer {access_token}"}

        metadata = {"name": uploaded_file.name}
        files = {
            "metadata": (None, str(metadata), "application/json"),
            "file": uploaded_file,
        }

        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            return redirect(reverse("list_google_drive_files"))
        
        return JsonResponse({"error": "Upload failed"}, status=response.status_code)

    return render(request, "upload.html")
