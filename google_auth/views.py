from django.utils.timezone import now, timedelta
from django.contrib.auth import login, logout
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
import requests
import os
from .models import CustomUser
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
@api_view(["GET"])
@permission_classes([AllowAny])
def google_login(request):
    """Returns the Google OAuth URL for authentication."""
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        "response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid email profile https://www.googleapis.com/auth/drive.file"
        "&access_type=offline"
        "&prompt=consent"
    )
    return Response({"auth_url": auth_url})

@api_view(["GET"])
@permission_classes([AllowAny])
def google_callback(request):
    """Handles Google OAuth callback and returns user data."""
    code = request.GET.get("code")
    if not code:
        return Response({"error": "Authorization code missing"}, status=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(token_url, data=data, timeout=10)
        response.raise_for_status()
        token_info = response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch token: {e}")
        return Response({"error": "Failed to retrieve access token"}, status=500)

    if "error" in token_info:
        return Response({"error": token_info.get("error_description", "Unknown error")}, status=400)

    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token", None)  # May be None if already granted
    expires_in = token_info.get("expires_in", 3600)

    # Fetch user info
    try:
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(user_info_url, headers=headers, timeout=10)
        user_response.raise_for_status()
        user_data = user_response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch user info: {e}")
        return Response({"error": "Failed to retrieve user information"}, status=500)

    google_id = user_data.get("id")
    email = user_data.get("email")
    name = user_data.get("name")
    profile_picture = user_data.get("picture")

    if not email:
        return Response({"error": "Email not provided by Google"}, status=400)

    # Save or update user in database
    user, created = CustomUser.objects.get_or_create(email=email, defaults={
        "username": name,
        "google_id": google_id,
        "profile_image": profile_picture,
        "is_logged_in": True,
    })

    if not created:
        update_fields = {"is_logged_in": True}
        if refresh_token:  
            update_fields["refresh_token"] = refresh_token  
        CustomUser.objects.filter(id=user.id).update(**update_fields)

    # Log the user in
    login(request, user)

    # Store user session securely
    request.session["user_id"] = user.id
    request.session["is_authenticated"] = True
    request.session["expires_at"] = (now() + timedelta(seconds=expires_in)).isoformat()
    request.session.set_expiry(expires_in)

    return Response({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_image": user.profile_image,
        },
        "access_token": access_token,
        "expires_in": expires_in,
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def google_logout(request):
    """Logs out the user and revokes the Google OAuth token."""
    token = request.session.get("access_token")
    if token:
        try:
            requests.post("https://accounts.google.com/o/oauth2/revoke", params={"token": token}, timeout=5)
        except requests.RequestException as e:
            logger.error(f"Failed to revoke Google token: {e}")

    user_id = request.session.get("user_id")
    if user_id:
        CustomUser.objects.filter(id=user_id).update(is_logged_in=False)

    request.session.flush()
    logout(request)

    return Response({"message": "Logout successful"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """Returns logged-in user details."""
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile_image": user.profile_image,
        "is_logged_in": user.is_logged_in,
    })


