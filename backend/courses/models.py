from django.db import models
from majors.models import Major
from academic.models import Semester, University
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    code = models.CharField(max_length=50)

    major = models.ForeignKey(
        Major,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    #  علاقة many-to-many بين المادة والمينتورين
    mentors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="mentored_courses",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class CourseOffering(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="offerings"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="course_offerings"
    )

    #  المدرّس الأساسي للمادة في هذا الفصل
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supervised_courses"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.name} - {self.semester.name}"
    

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course_offering")

    def __str__(self):
        return f"{self.student.email} enrolled in {self.course_offering.course.name}"


class Lecture(models.Model):
    course_offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="lectures"
    )

    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to="lectures/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course_offering.course.name}"
