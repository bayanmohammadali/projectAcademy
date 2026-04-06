from os import major

from rest_framework.decorators import APIView, action
from rest_framework import generics, request
from rest_framework.permissions import AllowAny

from academic.signals import notify_students_and_mentors
from .serializers import CourseNameSerializer, CourseOfferingNameSerializer, CurrentSemesterEnrollmentSerializer, RegisterSerializer, StudentSemesterSerializer, SupervisorCreateSerializer, SupervisorSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin,IsSupervisor, IsStudent, IsMentor
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
    CourseOfferingSerializer,
    SemesterNameSerializer,
    EnrollmentSerializer,
    LectureSerializer,
    LectureNameSerializer,
    UserSerializer,
    GroupsSerializer,
    GroupNameSerializer,

)
from academic.models import AcademicYear, Semester, University
from majors.models import Major
from users.models import Notification, User
from groups.models import Group
from courses.models import Course, CourseOffering, Enrollment, Lecture
from majors.models import Major
from summaries.models import Summary
from mentors.models import MentorApplication

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


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
    permission_classes = [IsAuthenticated, IsAdmin]

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
    permission_classes = [IsAuthenticated, IsAdmin]

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
    permission_classes = [IsAuthenticated, IsAdmin]

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
    permission_classes = [IsAdmin]
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
    permission_classes = [IsAuthenticated, (IsSupervisor | IsAdmin | IsMentor | IsStudent)]

    def get_queryset(self):
        semester_id = self.kwargs.get("semester_id")
        return CourseOffering.objects.filter(semester_id=semester_id)

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
    def names(self, request, semester_id=None):
        offerings = CourseOffering.objects.filter(semester_id=semester_id)
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




class EnrollmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, (IsStudent | IsMentor)]

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
        course = Course.objects.get(id=course_id)
        mentors = course.mentors.all()

        data = [
            {
                "id": m.id,
                "name": m.full_name,
                "email": m.email
            }
            for m in mentors
        ]

        return Response(data)

    
    @action(detail=False, methods=["get"], url_path="groups_by_course/(?P<course_id>[^/.]+)")
    def groups_by_course(self, request, course_id=None):
        groups = Group.objects.filter(
            course_offering__course_id=course_id
        )

        data = GroupsSerializer(groups, many=True).data
        return Response(data)





    




class StudentSemesterView(APIView):
    permission_classes = [IsAuthenticated, (IsStudent | IsMentor)]

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


