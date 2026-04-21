from django.urls import path
from .views import  RegisterView
from .views import CourseOfferingViewSet, EnrollmentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import StudentSemesterView


urlpatterns = [

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # هون بينعرض للطلاب الفصول الدراسية
    path("student/semesters/", StudentSemesterView.as_view()),


]
# ---------------- Router ----------------
from rest_framework.routers import DefaultRouter
from.views import (
    AcademicYearViewSet,
    UniversityViewSet,
    MajorViewSet,
    NotificationViewSet,
    SemesterViewSet,
    CourseViewSet,
    UserViewSet,
    SupervisorViewSet,
    GroupViewSet,

)

router = DefaultRouter()

router.register("academic_years", AcademicYearViewSet, basename="academic_year") # هون بصير انشاء وعرض السنوات الدراسية اللي بتتبعها الفصول الدراسية
router.register("universities", UniversityViewSet, basename="university")
router.register("majors", MajorViewSet, basename="major")

#http://127.0.0.1:8000/api/supervisors/ - هون بطلعلي كل المشرفين اللي موجودين بالتطبيق + اضاقة مشرف جديد
#http://127.0.0.1:8000/api/supervisors/names/ - هون بطلعلي اسماء كل المشرفين الموجودين بالتطبيق
router.register("supervisors", SupervisorViewSet, basename="supervisor")


#http://127.0.0.1:8000/api/notifications/id/mark_as_read/ - هون بحدد الاشعار اللي بدي اعلمه مقروء
#http://127.0.0.1:8000/api/notifications/ رؤية كل الاشعارات تبعاايا حدا بالتطبيق حتى لو مشرف 
router.register("notifications", NotificationViewSet, basename="notification")


# http://127.0.0.1:8000/api/semesters/latest/ - هون بطلعلي الفصل الدراسي الحالي اللي active
#http://127.0.0.1:8000/api/semesters/names/ - هون بطلعلي اسماء كل الفصول الدراسية
router.register("semesters", SemesterViewSet, basename="semester")

#http://127.0.0.1:8000/api/courses/my_major/ #هون بطلعلي المواد يلي بتتبع تخصص معين 
router.register("courses", CourseViewSet, basename="course")

#http://127.0.0.1:8000/api/course_offerings/add_and_activate/ - هون بضيف مادة جديدة للفصل الدراسي الحالي وبفعلها مباشرة (للسوبرفايزر)
router.register("course_offerings", CourseOfferingViewSet, basename="course_offering")

#http://127.0.0.1:8000/api/enrollments/register/ - هون بسمح للطالب يسجل على مادة معينة في الفصل الدراسي الحالي
#http://127.0.0.1:8000/api/enrollments/current/ - هون بطلعلي المواد الفصل الحالي اللي الطالب مسجل عليها
#http://127.0.0.1:8000/api/enrollments/courses_by_semester/4مثال (id)/ - هون بطلعلي كل المواد اللي الطالب مسجل عليها في فصل دراسي معين
#http://127.0.0.1:8000/api/enrollments/lectures_by_course/4مثال (id)/ - هون بطلعلي كل المحاضرات اللي متعلقة بمادة معينة
#http://127.0.0.1:8000/api/enrollments/summaries_by_course/4مثال (id)/ - هون بطلعلي كل الملخصات اللي متعلقة بمادة معينة
#http://127.0.0.1:8000/api/enrollments/mentors_by_course/4مثال (id)/ - هون بطلعلي كل المينتورات اللي متعلقة بمادة معينة
#http://127.0.0.1:8000/api/enrollments/groups_by_course/4مثال (id)/ - هون بطلعلي كل المجموعات اللي متعلقة بمادة معينة
router.register("enrollments", EnrollmentViewSet, basename="enrollments") # هون بطلعلي كل المواد اللي الطالب مسجل عليها في الفصل الدراسي الحالي

# http://127.0.0.1:8000/api/users/admin_dashboard/ هون داش بورد تبع الادمن الاحصائيات عن المستخدمين بالتطبيق
#http://127.0.0.1:8000/api/users/supervisor_dashboard/  هون داش بورد تبع السوبرفايزر الاحصائيات عن المواد اللي بيشرف عليها والملخصات والطلبات تبع المينتورات  
router.register("users", UserViewSet, basename="users")

#_____________________________________________________________________________

router.register("groups", GroupViewSet, basename="group") # هون بطلعلي كل المجموعات اللي الطالب مشارك فيهـا


urlpatterns += router.urls