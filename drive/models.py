# from django.db import models

# # Create your models here.
# class DriveFile(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     file_id = models.CharField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
#     mime_type = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name
