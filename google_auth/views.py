from django.shortcuts import redirect, render
from django.utils.timezone import now, timedelta, make_aware
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
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
        "&access_type=offline"
        "&prompt=consent"
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
    profile_picture = user_data.get("picture")

    # Save or update user in database
    user, created = CustomUser.objects.get_or_create(email=email, defaults={
        "username": name,
        "google_id": google_id,
        "profile_image": profile_picture,
        "refresh_token": refresh_token,
        "is_logged_in": True,
    })

    if not created:
        if refresh_token:
            user.refresh_token = refresh_token
        user.is_logged_in = True
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
        return redirect("google_login")

    user = CustomUser.objects.get(id=user_id)
    return render(request, "success.html", {"username": user.username})

def google_logout(request):
    """ Logs the user out from Google and clears session. """
    token = request.session.get("access_token")
    if token:
        requests.post("https://accounts.google.com/o/oauth2/revoke", params={"token": token})

    # Update user status to logged out
    user_id = request.session.get("user_id")
    if user_id:
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_logged_in = False
            user.save()
        except CustomUser.DoesNotExist:
            pass

    # Clear session data
    request.session.flush()
    
    logout(request)
    return HttpResponseRedirect(reverse("logout"))

def logout_view(request):
    """ Renders the logout page. """
    return render(request, "logout.html")
