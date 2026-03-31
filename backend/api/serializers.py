from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from academic.models import University,AcademicYear, Semester
from majors.models import Major
from users.models import User
from groups.models import Group, GroupMember
from users.models import Notification
from courses.models import Course, CourseOffering, Enrollment



User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone_number",
            "image",
            "bio",
            "major",
            "university",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        validated_data["role"] = "student"
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user
    
class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = "__all__"


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = "__all__"


class SupervisorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "major"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(
            **validated_data,
            role="supervisor"
        )
        user.set_password(password)
        user.save()
        return user

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "major"]
    

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = "__all__"

class SemesterNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["id", "name"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields ="__all__"

class CourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name"]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class CourseOfferingBulkSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        supervisor = self.context["supervisor"]
        semester_id = self.context["semester_id"]

        offerings = []
        for item in validated_data:
            offering = CourseOffering.objects.create(
                course=item["course"],
                supervisor=supervisor,
                semester_id=semester_id
            )
            offerings.append(offering)
        return offerings

class CourseOfferingSerializer(serializers.ModelSerializer):
    semester = serializers.PrimaryKeyRelatedField(read_only=True)
    supervisor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CourseOffering
        fields = ["id", "course", "semester", "supervisor", "created_at"]
        list_serializer_class = CourseOfferingBulkSerializer

    def validate(self, data):
        course = data["course"]
        semester = self.context["semester_id"]

        if CourseOffering.objects.filter(course=course, semester=semester).exists():
            raise serializers.ValidationError(
                {"error": "This course is already offered in this semester."}
            )
        return data

class CourseOfferingNameSerializer(serializers.ModelSerializer):
    course = CourseNameSerializer(read_only=True)

    class Meta:
        model = CourseOffering
        fields= ['id','course']

class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class GroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "course_offering"]

    def create(self, validated_data):
        user = self.context["user"]

        # إذا many=True → validated_data list
        if isinstance(validated_data, list):
            enrollments = []
            for item in validated_data:
                enrollment = self._enroll_user(user, item)
                if enrollment:
                    enrollments.append(enrollment)
            return enrollments

        return self._enroll_user(user, validated_data)

    def _enroll_user(self, user, data):
        course_offering = data["course_offering"]

        # منع التسجيل المكرر
        if Enrollment.objects.filter(student=user, course_offering=course_offering).exists():
            return None

        # تسجيل الطالب أو المينتور كـ "مسجّل بالمادة"
        enrollment = Enrollment.objects.create(
            student=user,
            course_offering=course_offering
        )

        # إضافة المستخدم (طالب أو مينتور) لغروبات المادة
        from groups.models import GroupMember
        for group in course_offering.groups.all():
            GroupMember.objects.get_or_create(group=group, user=user)

        return enrollment


# عم جيب المواد الفصل الحالي
class CurrentSemesterEnrollmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    course_id = serializers.IntegerField(source="course_offering.course.id")
    course_name = serializers.CharField(source="course_offering.course.name")

    class Meta:
        model = Enrollment
        fields = ["id", "course_id", "course_name"]

#تعرض الفصول يلي طالب سجل فيها
class StudentSemesterSerializer(serializers.ModelSerializer):
    academic_year = serializers.CharField(source="academic_year.name")

    class Meta:
        model = Semester
        fields = ["id", "name", "academic_year"]

