from django.db import models
from django.conf import settings

class MentorApplication(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor_applications"
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="mentor_applications",
        null=True, blank=True
    )

    motivation_text = models.TextField()
    experience_text = models.TextField()

    STATUS_CHOICES = [
    ("pending", "Pending"),
    ("trial", "Trial"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]
    status = models.CharField(max_length=50, default="pending")  #  / approve / reject / Trial 
    ai_score = models.FloatField(null=True, blank=True)

    file1 = models.FileField(upload_to="mentor_applications/", null=True, blank=True)

    file2 = models.FileField(upload_to="mentor_applications/", null=True, blank=True)

    review_note = models.TextField(null=True, blank=True)

    trial_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")  #  يمنع التكرار

    def __str__(self):
        return f"Application by {self.student.email} for {self.course.name}"


class Session(models.Model):
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    course_offering = models.ForeignKey(
        "courses.CourseOffering",
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True, blank=True
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    session_date = models.DateTimeField()
    duration = models.IntegerField()  # minutes

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SessionParticipant(models.Model):
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="joined_sessions"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} joined {self.session.title}"


class MentorRating(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor_ratings"
    )

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_ratings"
    )

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="mentor_ratings"
    )

    rating_value = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating_value} for {self.mentor.email}"


class CourseMentorRecommendation(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_recommendations"
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="mentor_recommendations"
    )

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recommended_for"
    )

    score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation: {self.mentor} for {self.student} in {self.course}"
