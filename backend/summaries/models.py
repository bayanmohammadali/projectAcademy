from django.db import models
from django.conf import settings
from courses.models import Lecture

class Summary(models.Model):
    title = models.CharField(max_length=255)

    file = models.FileField(
        upload_to="summaries/",
        null=True,
        blank=True
    )

    status = models.CharField(max_length=50)

    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.CASCADE,
        related_name="summaries"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_summaries"
    )

    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="locked_summaries"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class SummaryVersion(models.Model):
    summary = models.ForeignKey(
        Summary,
        on_delete=models.CASCADE,
        related_name="versions"
    )

    file_path = models.FileField(
        upload_to="summary_versions/",
        null=True,
        blank=True
    )

    version_number = models.IntegerField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.summary.title} - v{self.version_number}"

class SummaryReview(models.Model):
    summary_version = models.ForeignKey(
        SummaryVersion,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summary_reviews"
    )

    status = models.CharField(max_length=50)
    notes = models.TextField()

    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.summary_version}"

class SummaryRating(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summary_ratings"
    )

    summary_version = models.ForeignKey(
        SummaryVersion,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    rating_value = models.IntegerField()
    comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating_value} for {self.summary_version}"



# summaries/models.py

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )

    lecture = models.ForeignKey(
        "courses.Lecture",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favorited_by"
    )

    summary = models.ForeignKey(
        "summaries.Summary",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favorited_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.lecture:
            return f"{self.user.email} favorited lecture {self.lecture.title}"
        if self.summary:
            return f"{self.user.email} favorited summary {self.summary.title}"
        return f"Favorite by {self.user.email}"

