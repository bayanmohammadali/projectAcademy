from rest_framework.permissions import BasePermission
from mentors.models import MentorApplication

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and request.user.role == "admin"
        )

class IsSupervisor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and request.user.role == "supervisor"
        )

class IsStudent(BasePermission):
    def has_permission(self, request , view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and request.user.role == "student"
        )

def is_mentor(user):
    # نجيب آخر طلب Mentor قدّمه الطالب
    app = MentorApplication.objects.filter(student=user).order_by('-created_at').first()
    if not app:
        return False

    # Mentor تجريبي أو Mentor رسمي
    return app.status in ["trial", "approved"]

class IsTrialOrMentor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and is_mentor(request.user)
        )
