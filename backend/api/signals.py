from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Course,Lecture
from summaries.models import Summary
from .utils import send_notification



@receiver(post_save, sender=Course)
def notify_new_course(sender, instance, created, **kwargs):
    if created:
        # Loop through all students enrolled in this course
        for student in instance.students.all():
            send_notification(
                student,
                "New Course Added",
                f"A new course has been added: {instance.title}"
            )



@receiver(post_save, sender=Lecture)
def notify_new_lecture(sender, instance, created, **kwargs):
    if created:
        for student in instance.course.students.all():
            send_notification(
                student,
                "New Lecture Uploaded",
                f"A new lecture has been uploaded in {instance.course.title}"
            )



@receiver(post_save, sender=Summary)
def notify_new_summary(sender, instance, created, **kwargs):
    if created:
        for student in instance.course.students.all():
            send_notification(
                student,
                "New Summary Available",
                f"A new summary has been added for {instance.course.title}"
            )

