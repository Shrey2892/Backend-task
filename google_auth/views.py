from django.shortcuts import redirect,render
from django.contrib.auth import logout
from django.http import JsonResponse
import requests
import os
from dotenv import load_dotenv


load_dotenv()

def google_login(request):
    """ Redirects user to Google's OAuth 2.0 authentication page. """
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        "response_type=code"
        f"&client_id={os.getenv('GOOGLE_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}"
        "&scope=openid email profile"
    )
    return redirect(auth_url)

def googles_callback(request):
    """ Handles Google OAuth callback and fetches user info. """
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "Authorization code missing"}, status=400)

    # Step 1: Exchange authorization code for access token
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
        return JsonResponse({"error": token_info["error_description"]}, status=400)

    access_token = token_info.get("access_token")

    # Step 2: Fetch user information from Google
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    user_response = requests.get(user_info_url, headers=headers)
    user_data = user_response.json()

    # Extract user details
    username = user_data.get("name", "User")
    email = user_data.get("email", "N/A")
    profile_picture = user_data.get("picture", None)

    # Store user info in session
    request.session["username"] = username
    request.session["email"] = email
    request.session["profile_picture"] = profile_picture

    # ✅ Redirect to the success page with user data
    return render(request, "success.html", {"username": username, "profile_picture": profile_picture})


def google_callback(request):
    """ Handles Google OAuth callback and fetches user info. """
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "Authorization code missing"}, status=400)

    # Step 1: Exchange authorization code for access & refresh tokens
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
        return JsonResponse({"error": token_info["error_description"]}, status=400)

    # Store access & refresh tokens in session
    request.session["access_token"] = token_info.get("access_token")
    request.session["refresh_token"] = token_info.get("refresh_token")
    request.session["expires_in"] = token_info.get("expires_in")  # Token expiration time

    # Step 2: Fetch user information from Google
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    
    user_response = requests.get(user_info_url, headers=headers)
    user_data = user_response.json()

    # Store user details in session
    request.session["username"] = user_data.get("name", "User")
    request.session["email"] = user_data.get("email", "N/A")
    request.session["profile_picture"] = user_data.get("picture", None)

    return render(request, "success.html", {"username": user_data.get("name"), "profile_picture": user_data.get("picture")})



def logout_view(request):
    # Logout the user from Django
    logout(request)

    # Redirect to Google's logout endpoint (Optional, as Google doesn’t provide a strict logout URL)
    google_logout_url = "https://accounts.google.com/logout"

    # Redirect to home or login page after logout
    return redirect(google_logout_url)  
