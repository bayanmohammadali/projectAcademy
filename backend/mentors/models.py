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

    status = models.CharField(max_length=50, default="pending")
    ai_score = models.FloatField(null=True, blank=True)

    file1 = models.FileField(upload_to="mentor_applications/", null=True, blank=True)
    file2 = models.FileField(upload_to="mentor_applications/", null=True, blank=True)

    review_note = models.TextField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ⭐ منع تضارب المعالجة
    is_processing = models.BooleanField(default=False)

    processing_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processing_applications"
    )

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"Application by {self.student.email}"


class MentorRenewal(models.Model):
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="renewal_records"
    )

    course_offering = models.ForeignKey(
        "courses.CourseOffering",
        on_delete=models.CASCADE,
        related_name="mentor_renewals"
    )

    is_renewed = models.BooleanField(default=False)

    renewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="renewed_mentors"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Renewal for {self.mentor.email} in {self.course_offering}"


class ChatRoom(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_rooms"
    )

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor_rooms"
    )
    last_session_time = models.DateTimeField(null=True, blank=True)
    last_rating_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.student.email} ↔ {self.mentor.email}"
    
class ChatMessage(models.Model):
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    message = models.TextField()
    is_real_session = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    def __str__(self):
        return f"Message from {self.sender.email}"

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

    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="ratings",
        null=True,         
        blank=True  
    )

    rating_value = models.IntegerField()
    comment = models.TextField(null=True, blank=True)

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
