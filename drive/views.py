from google_auth.utils import refresh_access_token
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.http import JsonResponse

def upload_file(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']

        # Get or refresh the access token
        access_token = request.session.get("access_token") or refresh_access_token(request)
        if not access_token:
            return JsonResponse({"error": "User authentication required"}, status=401)

        creds = Credentials(access_token)
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': file.name}
        media = MediaIoBaseUpload(BytesIO(file.read()), mimetype=file.content_type, resumable=True)
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        return JsonResponse({"file_id": uploaded_file.get('id'), "message": "File uploaded successfully"})

    return JsonResponse({"error": "No file provided"}, status=400)
