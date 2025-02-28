from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.http import JsonResponse

def list_drive_files(request):
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list().execute()
    return JsonResponse(results)
