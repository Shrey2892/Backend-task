from rest_framework import serializers
from .models import GoogleDriveFile

class GoogleDriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleDriveFile
        fields = ["id", "file_id", "name", "created_at"]
