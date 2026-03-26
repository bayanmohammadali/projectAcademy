from django.db import models

from django.db import models
from django.conf import settings
from courses.models import CourseOffering

class StudyGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="study_groups"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)

class GroupMember(models.Model):
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

class GroupMessage(models.Model):
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_group_messages"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class GroupFile(models.Model):
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="files"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_group_files"
    )
    file = models.FileField(upload_to="group_files/")
    created_at = models.DateTimeField(auto_now_add=True)
