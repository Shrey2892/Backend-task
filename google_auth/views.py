from django.shortcuts import redirect, render
from django.utils.timezone import now, timedelta, make_aware
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.contrib.auth import login, logout
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def google_login(request):
    """ Redirects user to Google's OAuth 2.0 authentication page. """
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        "response_type=code"
        f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}"
        "&scope=openid email profile https://www.googleapis.com/auth/drive.file"
        "&access_type=offline"  # Ensures refresh_token is received
        "&prompt=consent"  # Forces Google to always return a refresh token
    )
    return redirect(auth_url)


def google_callback(request):
    """ Handles Google OAuth callback, fetches user info, and manages session. """
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Authorization code missing"}, status=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    token_info = response.json()

    if "error" in token_info:
        return JsonResponse({"error": token_info.get("error_description", "Unknown error")}, status=400)

    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")
    expires_in = token_info.get("expires_in", 3600)

    # Fetch user info
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_data = user_response.json()

    google_id = user_data.get("id")
    email = user_data.get("email")
    name = user_data.get("name")
    print(name)
    profile_picture = user_data.get("picture")

    # Save or update user in database
    user, created = CustomUser.objects.get_or_create(email=email, defaults={
        "username": name,
        "google_id": google_id,
        "profile_image": profile_picture,
        "refresh_token": refresh_token,
    })

    if not created and refresh_token:
        user.refresh_token = refresh_token
        user.save()

    # Log the user in
    login(request, user)

    # Store user session data
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email
    request.session["is_authenticated"] = True
    request.session["access_token"] = access_token
    request.session["refresh_token"] = refresh_token
    request.session["expires_at"] = (now() + timedelta(seconds=expires_in)).isoformat()
    request.session.set_expiry(expires_in)

    return redirect("login_view")

def login_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("google_login")  # Redirect to login if session is missing

    user = CustomUser.objects.get(id=user_id)
    return render(request, "success.html", {"username": user.username})  # Pass username



def refresh_access_token(request):
    """ Refreshes the access token using the refresh token if expired. """
    expires_at = request.session.get("expires_at")
    if expires_at:
        try:
            expires_at = make_aware(datetime.fromisoformat(expires_at))
        except ValueError:
            expires_at = None

    if not expires_at or now() >= expires_at:
        refresh_token = request.session.get("refresh_token")
        if not refresh_token:
            request.session.flush()
            return JsonResponse({"error": "Session expired. Please log in again."}, status=401)

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(token_url, data=data)
        token_info = response.json()

        if "error" in token_info:
            request.session.flush()
            return JsonResponse({"error": "Session expired. Please log in again."}, status=401)

        request.session["access_token"] = token_info.get("access_token")
        expires_in = token_info.get("expires_in", 3600)
        request.session["expires_at"] = (now() + timedelta(seconds=expires_in)).isoformat()
        request.session.set_expiry(expires_in)

    return request.session.get("access_token")


def get_google_user_infos(request):
    """ Fetches user info from Google API with token refresh handling. """
    access_token = refresh_access_token(request)
    if not isinstance(access_token, str):
        return access_token  # Return error if refresh failed

    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    return JsonResponse(response.json())


def get_google_user_info(request):
    """ Fetches user info from Google API with token refresh handling. """
    access_token = refresh_access_token(request)
    if not isinstance(access_token, str):
        return JsonResponse({"error": "Failed to refresh access token"}, status=401)

    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    
    if response.status_code == 200:
        return JsonResponse(response.json())  # Return user data
    else:
        return JsonResponse({"error": "Failed to fetch user info"}, status=400)


def list_google_drive_files(request):
    """Fetch and display user's Google Drive files."""
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect(reverse("google_login"))  # Redirect if not authenticated

    service = build("drive", "v3", credentials=Credentials(access_token))
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get("files", [])

    return render(request, "drive_files.html", {"files": files})


def google_logout(request):
    """ Logs the user out from Google and clears session. """
    token = request.session.get("access_token")
    if token:
        requests.post("https://accounts.google.com/o/oauth2/revoke", params={"token": token})
    
    # Clear session data
    request.session.flush()
    
    logout(request)  # Log out user from Django session
    return HttpResponseRedirect(reverse("logout"))  # Redirect to logout page


def logout_view(request):
    """ Renders the logout page. """
    return render(request, "logout.html")


def get_all_users(request):
    """ Fetch all users from the database. """
    users = list(CustomUser.objects.values())
    return JsonResponse({"users": users})
