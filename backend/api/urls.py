from django.urls import path
from .views import  FCMTokenView, RegisterView
from .views import CourseOfferingViewSet, EnrollmentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import StudentSemesterView


urlpatterns = [

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("fcm-token/", FCMTokenView.as_view()),



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
    LectureViewSet,
    UserViewSet,
    SupervisorViewSet,
    GroupViewSet,
    GroupMessageViewSet,
    MentorApplicationViewSet,
    SummaryViewSet,
    MentorRenewalViewSet,
    FavoriteViewSet,
    ChatRoomViewSet,
    SurveyViewSet

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

#http://127.0.0.1:8000/api/semesters/latest/ - هون بطلعلي الفصل الدراسي الحالي اللي active
#http://127.0.0.1:8000/api/semesters/names/ - هون بطلعلي اسماء كل الفصول الدراسية
#http://127.0.0.1:8000/api/semesters/<semester_id>/assign_supervisors/ - هون بسمح للادمن يحدد المشرفين اللي بيشرفوا على فصل دراسي معين
#http://127.0.0.1:8000/api/semesters/<semester_id>/majors_supervisors/ - هون بطلعلي كل المشرفين اللي بيشرفوا على فصل دراسي معين مع التخصصات اللي بيشرفوا عليها)
router.register("semesters", SemesterViewSet, basename="semester")

#http://127.0.0.1:8000/api/courses/my_major/ هون بطلعلي المواد يلي بتتبع تخصص معين 
#http://127.0.0.1:8000/api/courses/search/ - هون بطلعلي المواد اللي تطابق بحث معين
router.register("courses", CourseViewSet, basename="course")

#http://127.0.0.1:8000/api/course_offerings/add_and_activate/ - هون بضيف مادة جديدة للفصل الدراسي الحالي وبفعلها مباشرة (للسوبرفايزر)
#http://127.0.01:8000/api/course_offerings/<offering_id>/deactivate/ - هون بوقف مادة معينة في الفصل الدراسي الحالي (للسوبرفايزر)
#http://127.0.0.1:8000/api/course_offerings/ -عرض المواد المفعلة 
#http://127.0.0.1:8000/api/course_offerings/names/ - هون بطلعلي اسماء كل المواد المفعلة في الفصل الدراسي الحالي
#http://127.0.0.1:8000/api/course_offerings/<offering_id>/add_lecture/ - هون بضيف محاضرة ل مادة معينة
#http://127.0.0.1:8000/api/course_offerings/<offering_id>/remove_lecture/<lecture_id>/ - هون بحذف محاضرة من مادة معينة
#http://127.0.0.1:8000/api/course_offerings/<offering_id>/lectures/ - هون بطلعلي كل المحاضرات اللي بتتبع مادة معينة في الفصل الدراسي الحالي

router.register("course_offerings", CourseOfferingViewSet, basename="course_offering")


#http://127.0.0.1:8000/api/lectures/search/ - هون بطلعلي المحاضرات اللي تطابق بحث معين
router.register("lectures", LectureViewSet, basename="lecture") 


#http://127.0.0.1:8000/api/enrollments/register/ - هون بسمح للطالب  اضافة مادة معينة في الفصل الدراسي الحالي
#http://127.0.0.1:8000/api/enrollments/drop/ - هون بسمح للطالب حذف مادة معينة من الفصل الدراسي الحالي
#http://127.0.0.1:8000/api/enrollments/current/ - هون بطلعلي المواد الفصل الحالي اللي الطالب مسجل عليها
#http://127.0.0.1:8000/api/enrollments/courses_by_semester/<semester_id>/ - هون بطلعلي كل المواد اللي الطالب مسجل عليها في فصل دراسي معين
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/lectures/ - هون بطلعلي كل المحاضرات اللي متعلقة بمادة معينة
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/summaries/ - هون بطلعلي كل الملخصات اللي متعلقة بمادة معينة
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/mentors/ - هون بطلعلي كل المينتورات اللي متعلقة بمادة معينة
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/download/lecture/<lecture_id> - هون بسمح للطالب تحميل محاضرة معينة
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/download/summary/<summary_id> - هون بسمح للطالب تحميل ملخص معين
#archive:
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/archive/<course_id>/ - هون بيسمح للطالب رؤية المحاضرات والملخصات السابقة للمادة 
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/download/archive/lecture/<lecture_id>/ - هون بسمح للطالب تحميل محاضرة معينة من الارشيف
#http://127.0.0.1:8000/api/enrollments/<enrollment_id>/download/archive/summary/<summary_id>/ - هون بسمح للطالب تحميل ملخص معين من الارشيف
router.register("enrollments", EnrollmentViewSet, basename="enrollments") # هون بطلعلي كل المواد اللي الطالب مسجل عليها في الفصل الدراسي الحالي

#http://127.0.0.1:8000/api/users/admin_dashboard/ هون داش بورد تبع الادمن الاحصائيات عن المستخدمين بالتطبيق
#http://127.0.0.1:8000/api/users/supervisor_dashboard/  هون داش بورد تبع السوبرفايزر الاحصائيات عن المواد اللي بيشرف عليها والملخصات والطلبات تبع المينتورات  
router.register("users", UserViewSet, basename="users")

#_____________________________________________________________________________
#ادارة للغروبات 
#chats:
#http://127.0.0.1:8000/api/groups/<group_id>/messages/ - هون بطلعلي كل الرسائل اللي موجودة في المجموعات اللي الطالب مشارك فيها
#http://127.0.0.1:8000/api/groups/<group_id>/send_message/ - هون الطالب ارسال رسالة ل مجموعة معينة
#groups:
#http://127.0.0.1:8000/api/groups/my_groups/<course_id>/ - هون بطلعلي كل المجموعات اللي الطالب مشارك فيها واللي بتتبع مادة معينة
router.register("groups", GroupViewSet, basename="group") # هون بطلعلي كل المجموعات اللي الطالب مشارك فيهـا
router.register("groupMessages",GroupMessageViewSet, basename="groupMessage") #ادارة لرسائل المجموعات 
#____________________________________________________________
#mentor
#http://127.0.0.1:8000/api/mentor_applications/apply/ - هون بسمح للطالب تقديم طلب مينتور لمادة معينة
#http://127.0.0.1:8000/api/mentor_applications/my_applications/ - الطالب يشوف طلباته
#http://127.0.0.1:8000/api/mentor_applications/pending/ - هون بطلعلي كل طلبات المينتورات اللي قدمت على مادة معينة واللي لسا ما انقبلت ولا رفضت (للسوبرفايزر)
#http://127.0.0.1:8000/api/mentor_applications/<application_id>/details/ - هون بطلعلي تفاصيل طلب مينتور معين (للسوبرفايزر)
#http://127.0.0.1:8000/api/mentor_applications/<application_id>/review/ - هون السوبرفايزر يقدر يوافق او يرفض طلب مينتور معين
#http://127.0.0.1:8000/api/mentor_applications/<application_id>/final_decision/ - هون السوبرفايزر يقدر يوافق بشكل نهائي او يرفض طلب مينتور معين بعد فترة التجريب (للسوبرفايزر)
#http://127.0.0.1:8000/api/mentor_applications/<application_id>/ai_score/ - هون السوبرفايزر يعطي AI Score لطلب مينتور معين (للسوبرفايزر)
#للمينورات الرسميين
#http://127.0.0.1:8000/api/mentor_applications/approved_by_course/<course_id>/ - المينتورات الموافق عليهم لمادة معيّنة
#http://127.0.0.1:8000/api/mentor_applications/approved_by_mentor/ - هون بطلعلي كل المينتورات اللي تم الموافقة عليهم من قبل سوبرفايزر اختصاص (مش شرط يكونوا تحت اشرافه)
#للمينتورات التجريبيين
#http://127.0.0.1:8000/api/mentor_applications/trial_by_course/<course_id>/ - المينتورات التجريبيين لمادة معيّنة
#http://127.0.0.1:8000/api/mentor_applications/trial_by_supervisor/ - هون بطلعلي كل المينتورات التجريبيين اللي تحت اشراف سوبرفايزر اختصاص 
#http://127.0.0.1:8000/api/mentor_applications/profile/ - هون المينتور يقدر يشوف ملفه الشخصي (للمينتور)

router.register("mentor_applications", MentorApplicationViewSet, basename="mentor_application") # هون بطلعلي كل طلبات المينتورات اللي قدمت على مادة معينة
#__________________________________
#تجديد المينتورات:
#http://127.0.0.1:8000/api/mentor_renewals/renewal_list/ - عرض كل المينتورات اللي لازم يقرر تجديدهم
#http://127.0.0.1:8000/api/mentor_renewals/<mentor_renewals_id>/renew/ -اتخاذ القرار (تجديد / رفض) لتجديد مينتور معين
#http://127.0.0.1:8000/api/mentor_renewals/renewed_approved/ - عرض كل المينتورات اللي تم تجديدهم
router.register("mentor_renewals", MentorRenewalViewSet, basename="mentor_renewal") # هون بطلعلي كل طلبات تجديد المينتورات اللي تحت اشراف سوبرفايزر اختصاص
#_______________________________________
#mentor Sumary:
#http://127.0.0.1:8000/api/summaries/search/ - هون بطلعلي الملخصات اللي تطابق بحث معين
#http://127.0.0.1:8000/api/summaries/create/ - هون بسمح للطالب اضافة ملخص جديد لمادة معينة
#http://127.0.0.1:8000/api/summaries/my-summaries/ - هون بطلعلي كل الملخصات اللي انا ضفتها كطالب
#http://127.0.0.1:8000/api/summaries/<summary_id>/new-version/ - هون بسمح للطالب اضافة نسخة جديدة من ملخص معين
#http://127.0.0.1:8000/api/summaries/<summary_id>/versions/ - هون بطلعلي كل النسخ اللي تم اضافتها لملخص معين

#student:
#http://127.0.0.1:8000/api/summaries/<summary_id>/rate/ - هون بسمح للطالب تقييم ملخص معين
#supervisor:
# http://127.0.0.1:8000/api/summaries/pending/ - هون بطلعلي كل الملخصات اللي لسا ما انقبلت ولا رفضت لمادة معينة (للسوبرفايزر)
#http://127.0.0.1:8000/api/summaries/<summary_id>/review/ - هون السوبرفايزر يقدر يوافق او يرفض ملخص معين
router.register("summaries", SummaryViewSet, basename="summary") # هون بطلعلي كل الملخصات اللي بتتبع مادة معينة

#______________________
#Favorite:
#http://127.0.0.1:8000/api/favorites/list_favorites/ - هون بطلعلي كل المحاضرات والملخصات اللي ضفتها كطالب للمفضلة
#http://127.0.0.1:8000/api/favorites/add/
#http://127.0.0.1:8000/api/favorites/remove/
router.register("favorites", FavoriteViewSet, basename="favorite") # هون بطلعلي ك المفضلة اللي ضفتها كطالب

#____________________-
#ChatRoom:محادثات بين الطلاب والمينتورات
#http://127.0.0.1:8000/api/chat_rooms/ - هون بطلعلي كل غرف المحادثة بيني وبين المينتورات اللي بتتبع المواد اللي انا مسجل عليها
#http://127.0.0.1:8000/api/chat_rooms/create_room/ - هون بسمح للطالب انشاء غرفة محادثة مع مينتور معين لمادة معينة 
#http://127.0.0.1:8000/api/chat_rooms/<room_id>/messages/ - هون بطلعلي كل الرسائل اللي موجودة في غرفة محادثة معينة
#http://127.0.0.1:8000/api/chat_rooms/<room_id>/send_message/ - هون بسمح للطالب ارسال رسالة ل غرفة محادثة معينة
#http://127.0.0.1:8000/api/chat_rooms/<room_id>/should_rate/ - هون بطلعلي اذا كان مسموح للطالب تقييم جلسة معينة مع مينتور معين بعد انتهاء الجلسة (مسموح مرة واحدة لكل جلسة)
#http://127.0.0.1:8000/api/chat_rooms/<room_id>/rate/ - بسمح للطالب تقييم 
#http://127.0.0.1:8000/api/chat_rooms/<room_id>/analyze_session/ - هون بسمح للطالب يطلب تحليل جلسة معينة من خلال الذكاء الاصطناعي (مسموح مرة واحدة لكل جلسة)

router.register("chat_rooms", ChatRoomViewSet, basename="chat_room") # هون بطلعلي كل غرف المحادثة بيني وبين المينتورات اللي بتتبع المواد اللي انا مسجل عليها
#______
#Survey
#http://127.0.0.1:8000/api/surveys/<survery_id>/questions/ - هون بطلعلي كل الاسئلة اللي موجودة في استبيان معين
#http://127.0.0.1:8000/api/surveys/<survery_id>/submit/ - هون بسمح للطالب يشارك في استبيان معين من خلال الاجابة على الاسئلة الموجودة فيه
#http://127.0.0.1:8000/api/surveys/<survery_id>/results/ - هون بطلعلي نتائج استبيان معين (للسوبرفايزر)
#http://127.0.0.1:8000/api/surveys/<survery_id>/check/ - هون بسمح للطالب يشوف اذا كان شارك في استبيان معين او لا
router.register("surveys", SurveyViewSet, basename="survey")
#_____
#Forget the password
urlpatterns += router.urls