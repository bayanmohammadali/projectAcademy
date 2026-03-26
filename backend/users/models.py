from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from academic.models import University
from majors.models import Major


########################################
# USER MANAGER
########################################
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


########################################
# USER MODEL
########################################
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("mentor", "Mentor"),
        ("supervisor", "Supervisor"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    bio = models.TextField(null=True, blank=True)

    is_approved = models.BooleanField(default=False)
    request_status = models.CharField(max_length=50, default="pending")

    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, related_name="users")
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, related_name="users")

    created_at = models.DateTimeField(default=timezone.now)

    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


# users/models.py

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    type = models.CharField(max_length=255) 
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.type}"
