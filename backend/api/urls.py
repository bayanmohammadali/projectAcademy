from django.urls import path
from .views import  RegisterView, SupervisorCreateView
from .views import CourseOfferingViewSet, EnrollmentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import StudentSemesterView, OfferingLectureView,OfferingLectureName, SupervisorNamesView


urlpatterns = [

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

     # إضافة مشرف
    path("supervisors/create/", SupervisorCreateView.as_view(), name="create-supervisor"),  #ادمن
    path("supervisors/names/", SupervisorNamesView.as_view(), name="supervisor-names"), # عرض أسماء المشرفين

    # عرض المواد المتاحة في فصل معيّن (للسوبرفايزر/الطالب/المينتور)
    path(
        "semesters/<int:semester_id>/course_offerings/names/",
        CourseOfferingViewSet.as_view({"get": "names"}),
        name="course-offering-names"
    ),
    # إضافة مواد للفصل الدراسي (السوبرفايزر)
    path(
        "semesters/<int:semester_id>/course_offerings/",
        CourseOfferingViewSet.as_view({"post": "create", "get": "list"}),
        name="semester-course-offerings"
    ),
    # تسجيل الطالب أو المينتور في مادة    
    path(
        "semesters/<int:semester_id>/course_offerings/register/",
        EnrollmentViewSet.as_view({"post": "register_course"}),
        name="student-register-course"
    ),
    # هون بينعرض للطلاب الفصول الدراسية
    path("student/semesters/", StudentSemesterView.as_view()),


    # عرض المحاضرات في مادة معينة (للسوبرفايزر/الطالب/المينتور)
    #واضافة محاضرة جديدة (للسوبرفايزر) 
    path(
        "course_offerings/<int:offering_id>/lectures/",
        OfferingLectureView.as_view(),
        name="course-offering-lectures"
    ),
    # عرض أسماء المحاضرات في مادة معينة (للسوبرفايزر/الطالب/المينتور)
    path(
        "course_offerings/<int:offering_id>/lectures/names/",
        OfferingLectureName.as_view(),
        name="course-offering-lecture-names"
    ),


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

)

router = DefaultRouter()

router.register("academic_years", AcademicYearViewSet, basename="academic_year")
router.register("universities", UniversityViewSet, basename="university")
router.register("majors", MajorViewSet, basename="major")
router.register("notifications", NotificationViewSet, basename="notification")
# http://127.0.0.1:8000/api/semesters/latest/ - هون بطلعلي الفصل الدراسي الحالي اللي active
#http://127.0.0.1:8000/api/semesters/names/ - هون بطلعلي اسماء كل الفصول الدراسية
router.register("semesters", SemesterViewSet, basename="semester")

router.register("courses", CourseViewSet, basename="course")
#http://127.0.0.1:8000/api/enrollments/current/ - هون بطلعلي المواد الفصل الحالي اللي الطالب مسجل عليها
router.register("enrollments", EnrollmentViewSet, basename="enrollments")

router.register("users", UserViewSet, basename="users")

urlpatterns += router.urls