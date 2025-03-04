from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class CustomUser(AbstractUser):
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    profile_image = models.URLField(max_length=500, null=True, blank=True)
    refresh_token = models.TextField(blank=True, default="")

    first_name = models.CharField(max_length=150, blank=True, null=True)  
    last_name = models.CharField(max_length=150, blank=True, null=True)   
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)  
    password = models.CharField(max_length=128, blank=True, null=True)  

    is_active = models.BooleanField(default=True)  # Ensure user can log in
    is_staff = models.BooleanField(default=False)  # Admin access flag
    is_superuser = models.BooleanField(default=False)  # Superuser flag
    last_login = models.DateTimeField(null=True, blank=True, default=now)

    groups = models.ManyToManyField("auth.Group", blank=True)
    user_permissions = models.ManyToManyField("auth.Permission", blank=True)

    def save(self, *args, **kwargs):
        if self.username and not self.first_name and not self.last_name:
            name_parts = self.username.split()
            self.first_name = name_parts[0] if len(name_parts) > 0 else ""
            self.last_name = name_parts[1] if len(name_parts) > 1 else ""
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email if self.email else self.username
