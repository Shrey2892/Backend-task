# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class CustomUser(AbstractUser):
#     google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
#     profile_image = models.URLField(null=True, blank=True)
#     refresh_token = models.TextField(null=True, blank=True)

#     # Fix related_name conflicts
#     groups = models.ManyToManyField(
#         "auth.Group",
#         related_name="customuser_set",  # Unique related name
#         blank=True
#     )
#     user_permissions = models.ManyToManyField(
#         "auth.Permission",
#         related_name="customuser_permissions_set",  # Unique related name
#         blank=True
#     )

#     def __str__(self):
#         return self.username
