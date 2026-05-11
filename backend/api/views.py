
from rest_framework.decorators import APIView, action
from rest_framework import generics, request
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework.decorators import action 
from academic.signals import notify_students_and_mentors
from .serializers import CourseNameSerializer, CourseOfferingNameSerializer, CurrentSemesterEnrollmentSerializer, RegisterSerializer, StudentSemesterSerializer, SupervisorCreateSerializer, SupervisorSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from .utils import send_notification


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin,IsSupervisor, IsStudent, IsTrialOrMentor
from .serializers import (
    UniversitySerializer,
    UniversityNamesSerializer,
    MajorSerializer,
    MajorNamesSerializer,
    AcademicYearSerializer,
    AcademicYearNamesSerializer,
    NotificationSerializer,
    SemesterSerializer,
    CourseSerializer,
    LectureSerializer,
    LectureNameSerializer,
    CourseOfferingSerializer,
    SemesterNameSerializer,
    EnrollmentSerializer,
    LectureSerializer,
    LectureNameSerializer,
    UserSerializer,
    GroupsSerializer,
    GroupNameSerializer,
    MentorApplicationSerializer,
    SummarySerializer,
    SummaryNameSerializer,
    SummaryReviewSerializer,
    SummaryVersionSerializer,


)
from academic.models import AcademicYear, Semester, University
from majors.models import Major
from users.models import Notification, User
from groups.models import Group, GroupMessage, GroupFile, GroupMember
from courses.models import Course, CourseOffering, Enrollment, Lecture
from majors.models import Major
from summaries.models import Summary
from mentors.models import MentorApplication
from summaries.models import Summary, SummaryVersion, SummaryReview, SummaryRating

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data["id"])

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": response.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # فقط الأدمن يضيف مستخدمين
        if request.user.role != "admin":
            return Response({"error": "Only admin can create users"}, status=403)

        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "User updated successfully",
            "user": response.data 
        })
        
    def destroy(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response({"error": "Only admin can delete users"}, status=403)
        return super().destroy(request, *args, **kwargs)


    @action(detail=False, methods=["get"], url_path="students_and_mentors")
    def students_and_mentors(self, request):
        users = User.objects.filter(role__in=["student", "mentor"])
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="dashboard_stats")
    def admin_dashboard(self, request):
        # عدد الطلاب + المينتورات
        students_and_mentors = User.objects.filter(role__in=["student", "mentor"]).count()

        # عدد الجامعات
        universities = University.objects.count()

        # عدد المواد
        courses = Course.objects.count()

     # عدد السوبرفايزرات
        supervisors = User.objects.filter(role="supervisor").count()

        return Response({
            "students_and_mentors": students_and_mentors,
            "universities": universities,
            "courses": courses,
            "supervisors": supervisors
        })
    
    @action(detail=False, methods=["get"], url_path="supervisor_dashboard")
    def supervisor_dashboard(self, request):
        user = request.user

    # تأكد أنه سوبرفايزر
        if user.role != "supervisor":
            return Response({"error": "Only supervisors can access this dashboard"}, status=403)

    # اختصاص السوبرفايزر
        major = user.major
        if not major:
            return Response({"error": "Supervisor has no major assigned"}, status=400)

    # عدد المينتورات في نفس الاختصاص
        mentors_count = User.objects.filter(role="mentor", major=major).count()

    # عدد المواد التابعة للاختصاص
        courses_count = Course.objects.filter(major=major).count()

    # عدد الملخصات الخاصة باختصاص السوبرفايزر
        summaries_count = Summary.objects.filter(
        lecture__course_offering__course__major__name=major
    ).count()


    # عدد طلبات المينتورات الخاصة باختصاص السوبرفايزر
        mentor_requests = MentorApplication.objects.filter(
            course__major=major
        ).count()

        return Response({
            "mentors_count": mentors_count,
            "courses_count": courses_count,
            "summaries_count": summaries_count,
            "mentor_requests": mentor_requests
      })

    

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [AllowAny()]   # أي مستخدم مسجّل
        return [IsAuthenticated(), IsAdmin()]  # فقط الإدمن

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        academic_year = serializer.save()

        return Response({
            "message": "Academic year created successfully",
            "academic_year": serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Academic year updated successfully",
            "academic_year": response.data
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Academic year deleted successfully"
        })
    
    def names(self, request):
        academic_years = AcademicYear.objects.all()
        serializer = AcademicYearNamesSerializer(academic_years, many=True)
        return Response(serializer.data)
    

 

class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [AllowAny()]   # أي مستخدم مسجّل
        return [IsAuthenticated(), IsAdmin()]  # فقط الإدمن

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        university = serializer.save()

        return Response({
            "message": "University created successfully",
            "university": serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "University updated successfully",
            "university": response.data
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "message": "University deleted successfully"
        })
    
    def names(self, request):
        universities = University.objects.all()
        serializer = UniversityNamesSerializer(universities, many=True)
        return Response(serializer.data)

class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.all()
    serializer_class = MajorSerializer
    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [AllowAny()]   # أي مستخدم مسجّل
        return [IsAuthenticated(), IsAdmin()]  # فقط الإدمن

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        major = serializer.save()

        return Response({
            "message": "Major created successfully",
            "major": serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Major updated successfully",
            "major": response.data
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Major deleted successfully"
        })
    
    def names(self, request):
        majors = Major.objects.all()
        serializer = MajorNamesSerializer(majors, many=True)
        return Response(serializer.data)



class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role="supervisor")
    serializer_class = SupervisorCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supervisor = serializer.save()

        return Response({
            "message": "Supervisor created successfully",
            "supervisor": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Supervisor updated successfully",
            "supervisor": response.data
        })
    
    @action(detail=False, methods=['get'])
    def names(self, request):
        supervisors = User.objects.filter(role="supervisor")
        serializer = SupervisorSerializer(supervisors, many=True)
        return Response(serializer.data)

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        semester = serializer.save()
        semester.is_active = True
        semester.save()

        Semester.objects.exclude(id=semester.id).update(is_active=False)
        return Response({
            "message": "Semester created successfully. Notifications sent to supervisors.",
            "semester": serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        # نحفظ الفصل
        instance = serializer.save()

        # إذا تم تفعيل هذا الفصل → نطفي كل الفصول الثانية
        if instance.is_active:
            Semester.objects.exclude(id=instance.id).update(is_active=False)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Semester updated successfully",
            "semester": response.data
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Semester deleted successfully"})

    @action(detail=False, methods=['get'])
    def names(self, request):
        semesters = Semester.objects.all()
        serializer = SemesterNameSerializer(semesters, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="latest")
    def latest_semester(self, request):
        latest = Semester.objects.filter(is_active=True).first()
        if not latest:
            return Response({"error": "No active semester found"}, status=404)

        serializer = self.get_serializer(latest)
        return Response(serializer.data)

    

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [IsAuthenticated()]   # أي مستخدم مسجّل
        return [IsAuthenticated(), IsAdmin()]  # فقط الإدمن

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return Response({
            "message": "Course created successfully",
            "course": serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Course updated successfully",
            "course": response.data
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Course deleted successfully"
        })
    
    @action(detail=False, methods=['get'])
    def names(self, request):
        courses = Course.objects.all()
        serializer = CourseNameSerializer(courses, many=True)
        return Response(serializer.data)
    

    # عرض المواد حسب التخصص (لما يختار الطالب تخصص معين، بطلع له المواد اللي بتتبع هذا التخصص)
    @action(detail=False, methods=["get"], url_path="my_major")
    def by_major(self, request):
        major_id = request.user.major_id 
        courses = Course.objects.filter(major_id=major_id)
        serializer = CourseNameSerializer(courses, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=["get"], url_path="search")
    def search_courses(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response({"error": "Search query is required"}, status=400)

        # الكل يشوف كل المواد
        courses = Course.objects.all()

        # فلترة حسب البحث فقط
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )

        serializer = CourseNameSerializer(courses, many=True)
        return Response(serializer.data)



 
class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsSupervisor]
    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [IsAuthenticated()]  
        return [IsAuthenticated(), IsSupervisor()]
    
    def get_queryset(self):
        queryset = Lecture.objects.all()
        return queryset

    

    def update(self, request, *args, **kwargs):
        lecture = self.get_object()
        serializer = LectureSerializer(lecture, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Lecture updated successfully"})
    
    def destroy(self, request, *args, **kwargs):
        lecture = self.get_object()
        lecture.delete()
        return Response({"message": "Lecture deleted successfully"})
    

    @action(detail=False, methods=["get"], url_path="names")
    def lecture_names(self, request):
        lectures = self.get_queryset()
        serializer = LectureNameSerializer(lectures, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="search")
    def search_lectures(self, request):
        keyword = request.query_params.get("q")

        if not keyword:
            return Response({"error": "Search keyword 'q' is required"}, status=400)

        lectures = Lecture.objects.filter(title__icontains=keyword)

        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data)





class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by("-created_at")
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)


class CourseOfferingViewSet(viewsets.ModelViewSet):
    serializer_class = CourseOfferingSerializer
    permission_classes = [IsAuthenticated, (IsSupervisor | IsAdmin | IsTrialOrMentor | IsStudent)]

    def get_queryset(self):
        semester = Semester.objects.filter(is_active=True).first()
        if not semester:
            return CourseOffering.objects.none()
        return CourseOffering.objects.filter(semester=semester,is_active=True)

    def create(self, request, *args, **kwargs):
        data = request.data
        semester_id = self.kwargs.get("semester_id")

        serializer = self.get_serializer(
            data=data,
            many=isinstance(data, list),
            context={
                "supervisor": request.user,
                "semester_id": semester_id
            }
        )

        serializer.is_valid(raise_exception=True)
        offerings = serializer.save()

        if isinstance(offerings, list):
            for offering in offerings:
                notify_students_and_mentors(offering)
        else:
            notify_students_and_mentors(offerings)

        return Response({
            "message": "Courses added successfully",
            "count": len(offerings) if isinstance(offerings, list) else 1
        }, status=status.HTTP_201_CREATED)
    

    @action(detail=False, methods=["get"])
    def names(self, request):
        offerings = CourseOffering.objects.filter(is_active=True)
        serializer = CourseOfferingNameSerializer(offerings, many=True)
        return Response(serializer.data)
    
#تفعيل المادة من قبل السوبرفايزر (لما يضغط على تفعيل المادة، بتصير متاحة للطلاب والمينتورين)
    @action(detail=False, methods=["post"], url_path="add_and_activate")
    def add_and_activate(self, request):
        course_id = request.data.get("course")
        if not course_id:
            return Response({"error": "Course ID is required"}, status=400)

    # نجيب الفصل النشط
        semester = Semester.objects.filter(is_active=True).first()
        if not semester:
            return Response({"error": "No active semester found"}, status=400)

    # ننشئ CourseOffering
        offering, created = CourseOffering.objects.get_or_create(
            course_id=course_id,
            semester=semester,
            supervisor=request.user
        )

    # نفعل المادة مباشرة
        offering.is_active = True
        offering.save()

        return Response({
            "message": "Course added and activated successfully",
            "offering_id": offering.id
        })


    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        offering = self.get_object()

        offering.is_active = False
        offering.save()

        return Response({
            "message": "Course offering deactivated successfully",
            "offering_id": offering.id
        })
    
    @action(detail=True, methods=["post"], url_path="add_lecture")
    def add_lecture(self, request, pk=None):
        user = request.user

        # فقط السوبرفايزر يضيف محاضرات
        if user.role != "supervisor":
            return Response({"error": "Only supervisors can add lectures"}, status=403)

        # 1) نجيب الـ offering
        try:
            offering = CourseOffering.objects.get(id=pk)
        except CourseOffering.DoesNotExist:
            return Response({"error": "Course offering not found"}, status=404)

        # 2) تجهيز البيانات
        data = request.data.copy()
        data["course_offering"] = offering.id

        # 3) إنشاء المحاضرة
        serializer = LectureSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        lecture = serializer.save()

        # 4) الرد
        return Response({
            "message": "Lecture added successfully",
            "lecture_id": lecture.id,
            "title": lecture.title,
            "file": lecture.file.url if lecture.file else None,
            "course_offering": offering.id
        }, status=201)
    

    @action(detail=True, methods=["get"], url_path="lectures")
    def get_lectures(self, request, pk=None):
        user = request.user

        # 1) نجيب الـ offering
        try:
            offering = CourseOffering.objects.get(id=pk, is_active=True)
        except CourseOffering.DoesNotExist:
            return Response({"error": "Course offering not found"}, status=404)

        # 2) الطالب والمينتور لازم يكونوا مسجلين بالمادة
        if user.role in ["student", "mentor"]:
            is_enrolled = Enrollment.objects.filter(
                student=user,
                course_offering=offering
            ).exists()

            if not is_enrolled:
                return Response(
                    {"error": "You are not enrolled in this course"},
                    status=403
                )

        # 3) جلب المحاضرات
        lectures = offering.lectures.all()

        data = [
            {
                "id": lec.id,
                "title": lec.title,
                "file": lec.file.url if lec.file else None,
                "created_at": lec.created_at
            }
            for lec in lectures
        ]

        return Response(data)
    
    @action(detail=True, methods=["delete"], url_path="remove_lecture/(?P<lecture_id>[^/.]+)")
    def remove_lecture(self, request, pk=None, lecture_id=None):
        user = request.user

        # فقط السوبرفايزر يقدر يحذف محاضرات
        if user.role != "supervisor":
            return Response({"error": "Only supervisors can delete lectures"}, status=403)

        # 1) تأكيد وجود الـ offering
        try:
            offering = CourseOffering.objects.get(id=pk)
        except CourseOffering.DoesNotExist:
            return Response({"error": "Course offering not found"}, status=404)

        # 2) تأكيد وجود المحاضرة ضمن نفس الـ offering
        try:
            lecture = Lecture.objects.get(id=lecture_id, course_offering=offering)
        except Lecture.DoesNotExist:
            return Response({"error": "Lecture not found in this course offering"}, status=404)

        # 3) حذف المحاضرة
        lecture.delete()

        return Response({"message": "Lecture removed successfully"}, status=200)
    
class EnrollmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, (IsStudent | IsTrialOrMentor)]

    def get_serializer_class(self):
        if self.action in ["current", "current_semester_courses"]:
            return CurrentSemesterEnrollmentSerializer
        return EnrollmentSerializer


    def get_queryset(self):
        user = self.request.user
        return Enrollment.objects.filter(student=user)   

    @action(detail=False, methods=["post"], url_path="register")
    def register_in_active_semester(self, request):
        course_id = request.data.get("course")
        if not course_id:
            return Response({"error": "Course ID is required"}, status=400)

    # 1) نجيب الفصل النشط
        semester = Semester.objects.filter(is_active=True).first()
        if not semester:
            return Response({"error": "No active semester found"}, status=400)

    # 2) نجيب الـ CourseOffering المفعّل
        try:
            offering = CourseOffering.objects.get(
                course_id=course_id,
                semester=semester,
                is_active=True
            )
        except CourseOffering.DoesNotExist:
            return Response({"error": "This course is not active in the current semester"}, status=400)

    # 3) نسجّل الطالب
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course_offering=offering
        )

        student = request.user


        return Response({
            "message": "Course registered successfully",
            "enrollment_id": enrollment.id
        })
    
    @action(detail=False, methods=["get"], url_path="courses_by_semester/(?P<semester_id>[^/.]+)")
    def courses_by_semester(self, request, semester_id=None):
        user = request.user

    # كل التسجيلات الخاصة بالطالب في هذا الفصل
        enrollments = Enrollment.objects.filter(
            student=user,
            course_offering__semester_id=semester_id
        )

    # استخراج المواد
        courses = [
            {
                "id": en.course_offering.course.id,
                "name": en.course_offering.course.name,
                "code": en.course_offering.course.code,
                "major": en.course_offering.course.major.name
            }
         for en in enrollments
        ]
        return Response(courses)
    
    @action(detail=False, methods=["get"], url_path="lectures_by_course/(?P<course_id>[^/.]+)")
    def lectures_by_course(self, request, course_id=None):
    
        user = request.user
        if user.role in ["student", "mentor"]:
            is_enrolled = Enrollment.objects.filter(
                student=user,
                course_offering__course_id=course_id
            ).exists()

        if not is_enrolled:
            return Response(
                {"error": "You are not enrolled in this course"},
                status=403
            )
        lectures = Lecture.objects.filter(
            course_offering__course_id=course_id
        )

        data = [
            {
                "id": lec.id,
                "title": lec.title,
                "file": lec.file.url if lec.file else None
            }
            for lec in lectures
        ]

        return Response(data)
    

    @action(detail=False, methods=["get"], url_path="summaries_by_course/(?P<course_id>[^/.]+)")
    def summaries_by_course(self, request, course_id=None):
        user = request.user

        if user.role in ["student", "mentor"]:
            is_enrolled = Enrollment.objects.filter(
                student=user,
                course_offering__course_id=course_id
            ).exists()

            if not is_enrolled:
                return Response(
                    {"error": "You are not enrolled in this course"},
                    status=403
                )
            
        summaries = Summary.objects.filter(
            lecture__course_offering__course_id=course_id
        )

        data = [
            {
                "id": s.id,
                "title": s.title,
                "file": s.file.url if s.file else None
            }
            for s in summaries
        ]

        return Response(data)
    
    @action(detail=False, methods=["get"], url_path="mentors_by_course/(?P<course_id>[^/.]+)")
    def mentors_by_course(self, request, course_id=None):
        user = request.user

        if user.role in ["student", "mentor"]:
            is_enrolled = Enrollment.objects.filter(
                student=user,
                course_offering__course_id=course_id
            ).exists()

            if not is_enrolled:
                return Response(
                    {"error": "You are not enrolled in this course"},
                    status=403
                )
            
        course = Course.objects.get(id=course_id)
        mentors = course.mentors.all()

        data = [
            {
                "id": m.id,
                "name": f"{m.first_name} {m.last_name}",
                "email": m.email
            }
            for m in mentors
        ]

        return Response(data)
    
    @action(detail=False, methods=["post"], url_path="drop")
    def drop_course(self, request):
        course_id = request.data.get("course")
        if not course_id:
            return Response({"error": "Course ID is required"}, status=400)

        # 1) نجيب الفصل النشط
        semester = Semester.objects.filter(is_active=True).first()
        if not semester:
            return Response({"error": "No active semester found"}, status=400)

        # 2) نجيب الـ CourseOffering
        try:
            offering = CourseOffering.objects.get(
                course_id=course_id,
                semester=semester
            )
        except CourseOffering.DoesNotExist:
            return Response({"error": "Course not found in this semester"}, status=404)

        # 3) نحذف التسجيل
        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course_offering=offering
            )
            enrollment.delete()
        except Enrollment.DoesNotExist:
            return Response({"error": "You are not enrolled in this course"}, status=400)

        # 4) نحذف الطالب من الغروبات
        GroupMember.objects.filter(
            group__course_offering=offering,
            user=request.user
        ).delete()

        return Response({"message": "Course dropped successfully"})





class StudentSemesterView(APIView):
    permission_classes = [IsAuthenticated, (IsStudent | IsTrialOrMentor)]

    def get(self, request):

        user = request.user

        # إذا كان طالب
        if user.role == "student":
            semesters = Semester.objects.filter(
                course_offerings__enrollments__student=user
            ).distinct()

        # إذا كان مينتور
        elif user.role == "mentor":
            semesters = Semester.objects.filter(
                course_offerings__mentors=user
            ).distinct()

        else:
            return Response({"error": "Unknown user role"}, status=400)

        serializer = StudentSemesterSerializer(semesters, many=True)
        return Response(serializer.data)


class OfferingLectureView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, offering_id):
        # عرض المحاضرات للجميع (طلاب، مينتور، سوبرفايزر)
        lectures = Lecture.objects.filter(course_offering_id=offering_id)
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data)

    def post(self, request, offering_id):
        user = request.user

        # فقط السوبرفايزر يضيف محاضرات
        if user.role != "supervisor":
            return Response({"error": "Only supervisors can add lectures"}, status=403)

        data = request.data.copy()
        data["course_offering"] = offering_id

        serializer = LectureSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)
    

class OfferingLectureName(APIView):
    permission_classes= [IsAuthenticated]

    def get (self, request, offering_id):
        lectures = Lecture.objects.filter(course_offering_id=offering_id)
        serializer = LectureNameSerializer(lectures, many=True)
        return Response(serializer.data)

#_____________________________________________________________________________

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(members__user=user)


    @action(detail=False, methods=["get"], url_path="by_course/(?P<course_id>[^/.]+)")
    def groups_by_course(self, request, course_id=None):
    # نجيب كل الـ CourseOffering التابعة للمادة
        offerings = CourseOffering.objects.filter(course_id=course_id)

    # نجيب كل المجموعات التابعة لهذه الـ offerings
        groups = Group.objects.filter(course_offering__in=offerings)

        serializer = GroupNameSerializer(groups, many=True)

        return Response(serializer.data)
    
    @action (detail=True, methods=["get"], url_path="messages")
    def group_messages(self, request, pk=None):
        group = self.get_object()
        messages = group.messages.all().order_by("created_at")

        data = [
            {
                "id": m.id,
                "sender": f"{m.sender.first_name} {m.sender.last_name}",
                "sender_id": m.sender.id,
                "message": m.message,
                "created_at": m.created_at
            }
            for m in messages
        ]
        return Response(data)
    
    @action(detail=True, methods=["post"], url_path="send_message")
    def send_message(self, request, pk=None):
        group = self.get_object()
        user = request.user
        message = request.data.get("message")

        # 1) إذا الفصل مو Active → ممنوع إرسال
        if not group.course_offering.is_active:
            return Response(
                {"detail": "This group is archived. You cannot send messages."},
                status=403
            )


         # 2) تأكد إنو الطالب عضو بهالغروب
        if not group.members.filter(user=user).exists():
            return Response(
                {"detail": "You are not a member of this group."},
                status=403
            )

        if not message:
            return Response({"detail": "Message is required."}, status=400)


        msg = GroupMessage.objects.create(
            group=group,
            sender=user,
            message=message
        )

        return Response({
            "id": msg.id,
            "sender": f"{msg.sender.first_name} {msg.sender.last_name}",
            "sender_id": msg.sender.id,
            "message": msg.message,
            "created_at": msg.created_at
        })
    
    @action(detail=False, methods=["get"], url_path="my_groups/(?P<course_id>[^/.]+)")
    def my_groups(self, request, course_id=None):
        user = request.user

        groups = Group.objects.filter(
            course_offering__course_id=course_id,
            members__user=user
        )
        data = []
        for g in groups:
            data.append({
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "is_active": g.course_offering.is_active,
                "created_at": g.created_at,
            })

        return Response(data)


class MentorApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = MentorApplicationSerializer
    permission_classes = [IsAuthenticated]

    # 1) فلترة الطلبات حسب الدور
    def get_queryset(self):
        user = self.request.user

        # الطالب يشوف طلباته فقط
        if user.role == "student":
            return MentorApplication.objects.filter(student=user)

        # السوبرفايزر يشوف طلبات طلابه فقط
        if user.role == "supervisor":
            return MentorApplication.objects.filter(student__supervisor=user)

        # الادمن يشوف الكل
        return MentorApplication.objects.all()

    # 2) الطالب يقدم طلب
    @action(detail=False, methods=["post"], url_path="apply")
    def apply(self, request):
        student = request.user
        course_id = request.data.get("course")
        motivation = request.data.get("motivation_text")
        experience = request.data.get("experience_text")

        if not course_id:
            return Response({"error": "Course ID is required"}, status=400)

        if MentorApplication.objects.filter(student=student, course_id=course_id).exists():
            return Response({"error": "You already applied for this course"}, status=400)

        application = MentorApplication.objects.create(
            student=student,
            course_id=course_id,
            motivation_text=motivation,
            experience_text=experience,
            status="pending"
        )

        file1 = request.FILES.get("file1")
        file2 = request.FILES.get("file2")

        # إعدادات التحقق
        MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
        allowed_types = ["application/pdf", "image/jpeg", "image/png"]

        # دالة للتحقق من الملف
        def validate_file(f):
            # حجم الملف
            if f.size > MAX_FILE_SIZE:
                return "File too large (max 25MB)"

            # نوع الملف
            if f.content_type not in allowed_types:
                return "Invalid file type"

            # التحقق من تلف الملف
            if f.content_type == "application/pdf":
                from PyPDF2 import PdfReader
                try:
                    PdfReader(f)
                except:
                    return "PDF file is corrupted"

            if f.content_type in ["image/jpeg", "image/png"]:
                from PIL import Image
                try:
                    Image.open(f).verify()
                except:
                    return "Image file is corrupted"

            return None

        # التحقق من file1
        if file1:
            error = validate_file(file1)
            if error:
                return Response({"error": f"file1: {error}"}, status=400)
            application.file1 = file1

        # التحقق من file2
        if file2:
            error = validate_file(file2)
            if error:
                return Response({"error": f"file2: {error}"}, status=400)
            application.file2 = file2

        application.save()


        return Response({
            "message": "Application submitted successfully",
            "application_id": application.id
        })

    # 3) الطالب يشوف طلباته
    @action(detail=False, methods=["get"], url_path="my_applications")
    def my_applications(self, request):
        apps = MentorApplication.objects.filter(student=request.user)
        serializer = MentorApplicationSerializer(apps, many=True)
        return Response(serializer.data)

    # 4) السوبرفايزر يشوف الطلبات المعلّقة
    @action(detail=False, methods=["get"], url_path="pending")
    def pending(self, request):
        user = request.user

        if user.role != "supervisor":
            return Response({"error": "Only supervisors can view pending applications"}, status=403)

        applications = MentorApplication.objects.filter(status="pending").order_by("-created_at")

        data = []
        for app in applications:
            data.append({
                "id": app.id,
                "student_id": app.student.id,
                "student_name": f"{app.student.first_name} {app.student.last_name}",
                "course_name": app.course.name if app.course else None,
                "created_at": app.created_at,
            })

        return Response({"pending_applications": data}, status=200)

    # 5) السوبرفايزر يشوف تفاصيل الطلب (المعلومات + الملفات)
    @action(detail=True, methods=["get"], url_path="details")
    def details(self, request, pk=None):
        user = request.user

        # فقط السوبرفايزر يشوف التفاصيل
        if user.role != "supervisor":
            return Response({"error": "Only supervisors can view application details"}, status=403)

        try:
            app = MentorApplication.objects.get(id=pk)
        except MentorApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=404)

        data = {
            "id": app.id,
            "student_id": app.student.id,
            "student_name": f"{app.student.first_name} {app.student.last_name}",
            "student_email": app.student.email,

            "course_id": app.course.id if app.course else None,
            "course_name": app.course.name if app.course else None,

            "motivation_text": app.motivation_text,
            "experience_text": app.experience_text,

            "file1": request.build_absolute_uri(app.file1.url) if app.file1 else None,
            "file2": request.build_absolute_uri(app.file2.url) if app.file2 else None,

            "status": app.status,
            "review_note": app.review_note,
            "created_at": app.created_at,
        }

        return Response(data, status=200)

    # 6) السوبرفايزر يراجع الطلب (قبول/رفض)
    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        user = request.user

        if user.role != "supervisor":
            return Response({"error": "Only supervisors can review applications"}, status=403)

        try:
            app = MentorApplication.objects.get(id=pk)
        except MentorApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=404)

        decision = request.data.get("decision")  # trial / reject
        note = request.data.get("review_note", "")

        if decision not in ["trial", "reject"]:
            return Response({"error": "Invalid decision"}, status=400)

        app.review_note = note

        if decision == "trial":
            app.status = "trial"
            app.trial_end_date = timezone.now() + timedelta(days=7)

            send_notification(
            app.student,
            "Trial Period Started",
            "You have been accepted as a trial mentor for 7 days."
        )
        else:
            app.status = "rejected"
            app.trial_end_date = None

            send_notification(
            app.student,
            "Application Rejected",
            "Unfortunately, your mentor application has been rejected."
        )

        app.save()

        return Response({
            "message": "Application reviewed successfully",
            "new_status": app.status,
            "trial_end_date": app.trial_end_date,
            "review_note": app.review_note
        }, status=200)

    # 7) الموافقة بشكل نهائي 
    @action(detail=True, methods=["post"], url_path="finalize")
    def finalize(self, request, pk=None):
        user = request.user

        # فقط السوبرفايزر
        if user.role != "supervisor":
            return Response({"error": "Only supervisors can finalize applications"}, status=403)

        # جلب الطلب
        try:
            app = MentorApplication.objects.get(id=pk)
        except MentorApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=404)

        decision = request.data.get("decision")  # approve / reject
        note = request.data.get("final_note", "")

        if decision not in ["approve", "reject"]:
            return Response({"error": "Invalid decision"}, status=400)

        # لازم يكون الطالب أصلاً في مرحلة التجربة
        if app.status != "trial":
            return Response({"error": "Application is not in trial phase"}, status=400)


        # إذا انتهت الفترة التجريبية
        if app.trial_end_date and app.trial_end_date < timezone.now():
            pass  # طبيعي، منكمّل

        # حفظ ملاحظة السوبرفايزر
        app.review_note = note

        # القرار النهائي
        if decision == "approve":
            app.status = "approved"

            student = app.student
            student.role = "mentor"
            student.save()

            send_notification(
            student,
            "Final Approval",
            "Congratulations! You are now an official mentor."
        )
                        
        else:
            app.status = "rejected"

            send_notification(
            app.student,
            "Trial Failed",
            "Unfortunately, you did not pass the trial period."
        )

        app.save()

        return Response({
            "message": "Final decision applied successfully",
            "new_status": app.status,
            "review_note": app.review_note,
            "role": app.student.role
        }, status=200)
    
    # 8) السوبرفايزر يعطي AI Score
    @action(detail=True, methods=["post"], url_path="ai_score")
    def ai_score_application(self, request, pk=None):
        if request.user.role != "supervisor":
            return Response({"error": "Only supervisors can score applications"}, status=403)

        app = self.get_object()
        score = request.data.get("score")

        try:
            score = float(score)
            if not (0 <= score <= 100):
                raise ValueError
        except (ValueError, TypeError):
            return Response({"error": "Score must be a number between 0 and 100"}, status=400)

        app.ai_score = score
        app.save()

        return Response({
            "message": "AI score assigned successfully",
            "application_id": app.id,
            "ai_score": app.ai_score
        })

    # 9) المينتورات الموافق عليهم لمادة معيّنة
    @action(detail=False, methods=["get"], url_path="approved_by_course/(?P<course_id>[^/.]+)")
    def approved_by_course(self, request, course_id=None):

        apps = MentorApplication.objects.filter(
            course_id=course_id,
            status="approved"
        )

        data = [
            {
                "id": app.student.id,
                "name": f"{app.student.first_name} {app.student.last_name}",
                "email": app.student.email
            }
            for app in apps
        ]

        return Response({"mentors": data})

    # 10) كل المينتورات الموافق عليهم عند هذا السوبرفايزر
    @action(detail=False, methods=["get"], url_path="approved_by_mentor")
    def approved_by_mentor(self, request):
        if request.user.role != "supervisor":
            return Response({"error": "Only supervisors can access this endpoint"}, status=403)

        apps = MentorApplication.objects.filter(
            status="approved",
        )

        data = [
            {
                "id": app.student.id,
                "name": f"{app.student.first_name} {app.student.last_name}",
                "email": app.student.email,
                "course": app.course.name if app.course else None
            }
            for app in apps
        ]

        return Response({"approved_mentors": data})

   #11) المينتورات التجريبيين
    @action(detail=False, methods=["get"], url_path="trial_by_course/(?P<course_id>[^/.]+)")
    def trial_by_course(self, request, course_id=None):
        apps = MentorApplication.objects.filter(course_id=course_id, status="trial")

        data = [
            {
                "id": app.student.id,
                "name": f"{app.student.first_name} {app.student.last_name}",
                "email": app.student.email,
                "trial_end_date": app.trial_end_date
            }
            for app in apps
        ]

        return Response({"trial_mentors": data})
    
    #12) 
    @action(detail=False, methods=["get"], url_path="trial_by_supervisor")
    def trial_by_supervisor(self, request):
        if request.user.role != "supervisor":
            return Response({"error": "Only supervisors can access this endpoint"}, status=403)

        apps = MentorApplication.objects.filter(
            status="trial",
            student__supervisor=request.user
        )

        data = [
            {
                "id": app.student.id,
                "name": f"{app.student.first_name} {app.student.last_name}",
                "email": app.student.email,
                "course": app.course.name if app.course else None,
                "trial_end_date": app.trial_end_date
            }
            for app in apps
        ]

        return Response({"trial_mentors": data})


class SummaryViewSet(viewsets.ModelViewSet):
    queryset = Summary.objects.all()
    serializer_class=SummarySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="search")
    def search_summaries(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response({"error": "Search query is required"}, status=400)

        summaries = Summary.objects.filter(
            Q(title__icontains=query) |
            Q(lecture__title__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query)
        ).order_by("-created_at")

        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["post"], url_path="create")
    def create_summary(self, request):
        user = request.user
        lecture_id = request.data.get("lecture")

        # 1) نجيب الـ Lecture
        try:
            lecture = Lecture.objects.get(id=lecture_id)
        except Lecture.DoesNotExist:
            return Response({"error": "Lecture not found"}, status=404)

        # 2) نتأكد إنو المستخدم مينتور (trial أو approved) لنفس الكورس
        is_mentor = MentorApplication.objects.filter(
            student=user,
            course=lecture.course_offering.course,
            status__in=["trial", "approved"]
        ).exists()

        if not is_mentor:
            return Response(
                {"error": "You are not allowed to upload summaries for this lecture"},
                status=403
            )

        # 3) إنشاء Summary
        summary = Summary.objects.create(
            title=request.data.get("title"),
            file=request.data.get("file"),
            status="pending",
            lecture=lecture,
            student=user
        )

        # 4) إنشاء أول نسخة SummaryVersion
        SummaryVersion.objects.create(
            summary=summary,
            file_path=summary.file,
            version_number=1,
            is_active=True
        )

        return Response({"message": "Summary submitted successfully"}, status=201)


    @action(detail=False, methods=["get"], url_path="my-summaries")
    def my_summaries(self, request):
        user = request.user

        # 1) نجيب ملخصات المينتور نفسه
        summaries = Summary.objects.filter(
            student=user
        ).order_by("-created_at")

        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data, status=200)



    @action(detail=False, methods=["get"], url_path="pending")
    def pending_summaries(self, request):
        user = request.user

        # السوبرفايزر فقط
        offerings = CourseOffering.objects.filter(supervisor=user)
        lectures = Lecture.objects.filter(course_offering__in=offerings)

        summaries = Summary.objects.filter(
            lecture__in=lectures,
            status="pending"
        ).order_by("-created_at")

        serializer = SummarySerializer(summaries, many=True)
        return Response(serializer.data, status=200)


    @action(detail=True, methods=["post"], url_path="review")
    def review_summary(self, request, pk=None):
        supervisor = request.user

        try:
            summary = Summary.objects.get(id=pk)
        except Summary.DoesNotExist:
            return Response({"error": "Summary not found"}, status=404)

        # تأكد إنو السوبرفايزر هو المسؤول عن المادة
        if summary.lecture.course_offering.supervisor != supervisor:
            return Response({"error": "Not authorized"}, status=403)

        status_value = request.data.get("status")  # approved / rejected
        notes = request.data.get("notes", "")

        # تحديث حالة الملخص
        summary.status = status_value
        summary.save()

        # النسخة الفعّالة
        active_version = summary.versions.filter(is_active=True).first()

        # إنشاء مراجعة
        SummaryReview.objects.create(
            summary_version=active_version,
            supervisor=supervisor,
            status=status_value,
            notes=notes
        )

        return Response({"message": "Review submitted"}, status=200)

    @action(detail=True, methods=["post"], url_path="new-version")
    def new_version(self, request, pk=None):
        user = request.user

        try:
            summary = Summary.objects.get(id=pk)
        except Summary.DoesNotExist:
            return Response({"error": "Summary not found"}, status=404)

        # 1) تأكد إنو المستخدم هو صاحب الملخص
        if summary.student != user:
            return Response({"error": "Not authorized"}, status=403)

        # 2) تعطيل النسخة الحالية
        summary.versions.filter(is_active=True).update(is_active=False)

        # 3) إنشاء نسخة جديدة
        new_version = SummaryVersion.objects.create(
            summary=summary,
            file_path=request.data.get("file"),
            version_number=summary.versions.count() + 1,
            is_active=True
        )

        # 4) إعادة حالة الملخص إلى pending
        summary.status = "pending"
        summary.save()

        return Response({"message": "New version submitted"}, status=201)
    
    @action(detail=True, methods=["get"], url_path="versions")
    def summary_versions(self, request, pk=None):
        try:
            summary = Summary.objects.get(id=pk)
        except Summary.DoesNotExist:
            return Response({"error": "Summary not found"}, status=404)

        versions = summary.versions.all().order_by("-version_number")

        data = []
        for v in versions:
            data.append({
                "id": v.id,
                "version_number": v.version_number,
                "file": v.file_path.url if v.file_path else None,
                "is_active": v.is_active,
                "created_at": v.created_at,
                "reviews": [
                    {
                        "status": r.status,
                        "notes": r.notes,
                        "reviewed_at": r.reviewed_at
                    }
                    for r in v.reviews.all()
                ],
                "ratings": [
                    {
                        "rating": rt.rating_value,
                        "comment": rt.comment,
                        "created_at": rt.created_at
                    }
                    for rt in v.ratings.all()
                ]
            })

        return Response(data, status=200)








