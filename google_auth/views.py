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
#from django.contrib.auth import login
#from .models import CustomUser

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
    """ Handles Google OAuth callback and fetches user info. """
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
    
    request.session["access_token"] = token_info.get("access_token")
    request.session["refresh_token"] = token_info.get("refresh_token")
    expires_in = token_info.get("expires_in", 3600)
    request.session["expires_at"] = (now() + timedelta(seconds=expires_in)).isoformat()
    request.session.set_expiry(expires_in)
    
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_data = user_response.json()
    
    request.session["username"] = user_data.get("name", "User")
    request.session["email"] = user_data.get("email", "N/A")
    request.session["profile_picture"] = user_data.get("picture", None)
    
    return render(request, "success.html", {"username": user_data.get("name"), "profile_picture": user_data.get("picture")})



def googles_callback(request):
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

    # Fetch user data from Google
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    user_response = requests.get(user_info_url, headers=headers)
    user_data = user_response.json()

    google_id = user_data.get("id")
    email = user_data.get("email")
    name = user_data.get("name")
    profile_picture = user_data.get("picture")

    # Save user to database
    user, created = CustomUser.objects.get_or_create(email=email, defaults={
        "username": name,
        "google_id": google_id,
        "profile_image": profile_picture,
        "refresh_token": refresh_token,
    })

    # Update refresh token if changed
    if not created and refresh_token:
        user.refresh_token = refresh_token
        user.save()

    login(request, user)  # Log the user in

    return JsonResponse({
        "message": "User authenticated successfully",
        "user": {
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_image,
        }
    })









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

def get_google_user_info(request):
    """ Fetches user info from Google API with token refresh handling. """
    access_token = refresh_access_token(request)
    if not isinstance(access_token, str):
        return access_token  # Return error if refresh failed
    
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    return JsonResponse(response.json())




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
    request.session.flush()
    return HttpResponseRedirect(reverse("logout"))  # Redirect to logout page

def logout_view(request):
    """ Renders the logout page. """
    return render(request, "logout.html")
