from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)

    # Override default Django auth fields if not needed
    groups = models.ManyToManyField("auth.Group", blank=True)
    user_permissions = models.ManyToManyField("auth.Permission", blank=True)

    def __str__(self):
        return self.username
