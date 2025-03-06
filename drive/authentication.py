from django.http import JsonResponse
from django.utils.timezone import now, timedelta, make_aware
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def refresh_access_token(request):
    """Refreshes the access token using the refresh token if expired."""
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

def get_access_token(request):
    """Gets a valid access token, refreshing if necessary."""
    access_token = request.session.get("access_token")
    if not access_token:
        return JsonResponse({"error": "Authentication required"}, status=401)

    return refresh_access_token(request)
