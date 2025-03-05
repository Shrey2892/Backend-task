import requests
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .models import GoogleDriveFile

load_dotenv()


def get_access_token(request):
    """Retrieves and refreshes access token if expired."""
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect(reverse("google_login"))

    return access_token


def list_google_drive_files(request):
    """Fetches the user's Google Drive files using direct API requests and stores them in the database."""
    access_token = get_access_token(request)
    if not isinstance(access_token, str):
        return access_token  # Redirect if no token

    url = "https://www.googleapis.com/drive/v3/files"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    files = response.json().get("files", [])

    # Save files to the database (if not already saved)
    for file in files:
        GoogleDriveFile.objects.get_or_create(
            user=request.user,
            file_id=file["id"],
            defaults={"name": file["name"]}
        )

    return render(request, "drive_files.html", {"files": files})


def download_google_drive_file(request, file_id):
    """Downloads a file from Google Drive."""
    access_token = get_access_token(request)
    if not isinstance(access_token, str):
        return access_token

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        file_obj = get_object_or_404(GoogleDriveFile, file_id=file_id)
        response_obj = HttpResponse(response.content, content_type="application/octet-stream")
        response_obj["Content-Disposition"] = f'attachment; filename="{file_obj.name}"'
        return response_obj
    
    return JsonResponse({"error": "Failed to download file"}, status=response.status_code)


def delete_google_drive_file(request, file_id):
    """Deletes a file from Google Drive and removes it from the database."""
    access_token = get_access_token(request)
    if not isinstance(access_token, str):
        return access_token

    url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        GoogleDriveFile.objects.filter(file_id=file_id).delete()
        return redirect(reverse("list_google_drive_files"))
    
    return JsonResponse({"error": "Failed to delete file"}, status=response.status_code)


@csrf_exempt
def upload_to_google_drive(request):
    """Uploads a file to Google Drive and saves it to the database."""
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
        response_data = response.json()

        if response.status_code == 200:
            file_data = response.json()
            GoogleDriveFile.objects.create(
                user=request.user,
                file_id=file_data["id"],
                name=file_data["name"]
            )
            return redirect(reverse("list_google_drive_files"))
        
        print("Google Drive Upload Error:", response_data)  # Logs error in terminal
        return JsonResponse({"error": "Upload failed", "details": response_data}, status=response.status_code)
        
        #return JsonResponse({"error": "Upload failed"}, status=response.status_code)

    return render(request, "upload.html")