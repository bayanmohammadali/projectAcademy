from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from academic.models import University,AcademicYear, Semester
from majors.models import Major
from users.models import User
from groups.models import Group, GroupMember
from users.models import Notification
from courses.models import Course, CourseOffering, Enrollment, Lecture
from mentors.models import MentorApplication
from summaries.models import Summary, SummaryVersion, SummaryReview, SummaryRating, Favorite

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
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
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"

class AcademicYearNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["id", "name"]

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = "__all__"
        
class UniversityNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ["id", "name"]

class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = "__all__"

class MajorNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ["id", "name"]

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


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = "__all__"
        read_only_fields = ["created_at"]

class LectureNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ["id", "title"]


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


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = "__all__"
        read_only_fields = ["created_at"]

class LectureNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ["id", "title"]
    

class MentorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorApplication
        fields = "__all__"
        read_only_fields = ["created_at", "status"]


class SummarySerializer(serializers.ModelSerializer):
    lecture_title = serializers.CharField(source="lecture.title", read_only=True)
    active_version = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    class Meta:
        model = Summary
        fields = [
            "id",
            "title",
            "status",
            "lecture_title",
            "file",
            "created_at",
            "active_version",
            "reviews",
            "ratings",
        ]

    def get_active_version(self, obj):
        version = obj.versions.filter(is_active=True).first()
        if version:
            return {
                "version_number": version.version_number,
                "file": version.file_path.url if version.file_path else None
            }
        return None

    def get_reviews(self, obj):
        active_version = obj.versions.filter(is_active=True).first()
        if not active_version:
            return []
        return [
            {
                "status": review.status,
                "notes": review.notes,
                "reviewed_at": review.reviewed_at
            }
            for review in active_version.reviews.all()
        ]

    def get_ratings(self, obj):
        active_version = obj.versions.filter(is_active=True).first()
        if not active_version:
            return []

        return [
            {
                "rating": rating.rating_value,
                "comment": rating.comment,
                "created_at": rating.created_at
            }
            for rating in active_version.ratings.all()
        ]


class SummaryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ["id", "title"]

class SummaryVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryVersion
        fields = "__all__"
        read_only_fields = ["created_at"]

class SummaryReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryReview
        fields = "__all__"
        read_only_fields = ["created_at", "status"]

class SummaryRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryRating
        fields = "__all__"
        read_only_fields = ["created_at"]