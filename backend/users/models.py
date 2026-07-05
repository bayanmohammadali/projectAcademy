from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from academic.models import University, AcademicYear
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

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    bio = models.TextField(null=True, blank=True)

    is_approved = models.BooleanField(default=False)
    request_status = models.CharField(max_length=50, default="none")

    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, related_name="users")
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, related_name="users", blank=True)

    is_primary_supervisor = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(null=True, blank=True)

    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).total_seconds() < 300  # 5 minutes

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
    related_id = models.IntegerField(null=True, blank=True)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.type}"
    

class FCMToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fcm_tokens")
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Survey(models.Model):
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="surveys",
        null=True
    )

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_surveys"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class SurveyQuestion(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    text = models.TextField()

    QUESTION_TYPES = [
        ("rating", "Rating"),
        ("choice", "Multiple Choice"),
    ]

    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default="choice")

    choices = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Q: {self.text}"

class SurveyAnswer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="survey_answers"
    )

    question = models.ForeignKey(
        SurveyQuestion,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    answer = models.TextField()  # نص، رقم، اختيار… كله يمشي

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")  # كل مستخدم يجاوب مرة واحدة فقط

    def __str__(self):
        return f"{self.user.email} → {self.question.text}"

