import os
import requests

def refresh_access_token(request):
    """ Refresh Google OAuth access token if expired. """
    refresh_token = request.session.get("refresh_token")
    if not refresh_token:
        return None  # No refresh token means user must re-authenticate

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(token_url, data=data)
    new_token_info = response.json()

    if "error" in new_token_info:
        return None  # Token refresh failed

    # Update session with new access token
    request.session["access_token"] = new_token_info.get("access_token")
    request.session["expires_in"] = new_token_info.get("expires_in")
    request.session.modified = True  # Ensure session updates persist

    return request.session["access_token"]
