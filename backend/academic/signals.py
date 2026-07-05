from django.db.models.signals import post_save
from django.dispatch import receiver
from academic.models import Semester
from users.models import User, Notification
from firebase.firebase import send_push_notification

@receiver(post_save, sender=Semester)
def notify_supervisors_on_new_semester(sender, instance, created, **kwargs):
    if created:
        supervisors = User.objects.filter(role="supervisor")
        for supervisor in supervisors:
            Notification.objects.create(
                user=supervisor,
                type="semester",
                message=f"A new semester '{instance.name}' has been opened. Please add your courses."
            )
            send_push_notification(
                supervisor,
                title="New Semester Opened",
                body=f"Semester '{instance.name}' has been opened. Please add your courses.",
            )




def notify_students_and_mentors(offering):
    course_name = offering.course.name

    # إشعار للطلاب
    students = User.objects.filter(role="student")
    for student in students:
        Notification.objects.create(
            user=student,
            type="course",
            message=f"New course '{course_name}' is now available for registration."
        )

    # إشعار للمينتور
    mentors = User.objects.filter(role="mentor")
    for mentor in mentors:
        Notification.objects.create(
            user=mentor,
            type="course",
            message=f"A new course '{course_name}' has been added to the semester."
        )
