from django.shortcuts import redirect
from django.http import JsonResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def google_login(request):
    auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri={os.getenv('GOOGLE_REDIRECT_URI')}&scope=openid email profile"
    return redirect(auth_url)

def google_callback(request):
    code = request.GET.get('code')
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
        'grant_type': 'authorization_code',
    }
    response = requests.post(token_url, data=data)
    return JsonResponse(response.json())
