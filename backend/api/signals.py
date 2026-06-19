from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import Course, Lecture
from summaries.models import Summary
from users.models import Notification
from firebase.firebase import send_push_notification


@receiver(post_save, sender=Course)
def notify_new_course(sender, instance, created, **kwargs):
    if created:
        for student in instance.students.all():

            # 1) حفظ الإشعار داخل قاعدة البيانات
            Notification.objects.create(
                user=student,
                type="new_course",
                message=f"A new course has been added: {instance.title}"
            )

            # 2) إرسال الإشعار إلى Firebase
            send_push_notification(
                student,
                title="New Course Added",
                body=f"A new course has been added: {instance.title}"
            )


@receiver(post_save, sender=Lecture)
def notify_new_lecture(sender, instance, created, **kwargs):
    if created:
        course_name = instance.course_offering.course.name
        course_id = instance.course_offering.course.id
        for enrollment in instance.course_offering.enrollments.all():
            student = enrollment.student
            Notification.objects.create(
                user=student,
                type="new_lecture",
                message=f"A new lecture has been uploaded in {course_name}",
                related_id=course_id
            )
            send_push_notification(
                student,
                title="New Lecture Uploaded",
                body=f"A new lecture has been uploaded in {course_name}"
            )


@receiver(post_save, sender=Summary)
def notify_new_summary(sender, instance, created, **kwargs):
    if created:
        course_name = instance.lecture.course_offering.course.name
        course_id = instance.lecture.course_offering.course.id
        for enrollment in instance.lecture.course_offering.enrollments.all():
            student = enrollment.student
            Notification.objects.create(
                user=student,
                type="new_summary",
                message=f"A new summary has been added for {course_name}",
                related_id=course_id
            )
            send_push_notification(
                student,
                title="New Summary Available",
                body=f"A new summary has been added for {course_name}"
            )
