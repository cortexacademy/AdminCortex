from datetime import timedelta
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from django.utils import timezone

# ---------------------------------------------------For Subject/Chapter serializer----------------------
User = get_user_model()


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        exclude = ["subjects"]


class SubjectSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True, source="chapter_set")

    class Meta:
        model = Subject
        fields = "__all__"


class SubjectWithoutChaptersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class ExamIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id"]


class SubjectWithExamSerializer(serializers.ModelSerializer):
    exams = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ["id", "name", "exams"]

    def get_exams(self, obj):
        return ExamIDSerializer(obj.exam_set.all(), many=True).data


class ExamIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id"]


class SubjectWithExamSerializer(serializers.ModelSerializer):
    exams = serializers.SerializerMethodField()
    chapters = ChapterSerializer(many=True, read_only=True, source="chapter_set")

    class Meta:
        model = Subject
        fields = ["id", "name", "exams", "imageURL", "chapters"]

    def get_exams(self, obj):
        return ExamIDSerializer(obj.exam_set.all(), many=True).data


# ---------------------------------------------------For question serializer----------------------
class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = "__all__"


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"


class OptionCorrectIncorrectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "is_correct"]


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = "__all__"


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = "__all__"


class AttemptSerializerWithDetailedOptions(serializers.ModelSerializer):
    selected_option = OptionCorrectIncorrectSerializer(many=True, read_only=True)

    class Meta:
        model = Attempt
        fields = ["id", "selected_option", "is_first"]


# Serializer for creating a new instance with limited fields (used for POST requests)
class AttemptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = ["question", "user", "is_first"]

    def create(self, validated_data):
        attempt = Attempt.objects.create(**validated_data)
        return attempt


# ---------------------------------------------------PYQ section-----------------------------


class ExamSerializer(serializers.ModelSerializer):
    subjects = SubjectWithoutChaptersSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = "__all__"
        # fields = ['id', 'name', 'subjects', 'created_at', 'updated_at', 'is_active']


# ---------------------------------------------------PYQ section-----------------------------
class ExamSerializer(serializers.ModelSerializer):
    subjects = SubjectWithoutChaptersSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = "__all__"
        # fields = ['id', 'name', 'subjects', 'created_at', 'updated_at', 'is_active']


class QuestionSerializer(serializers.ModelSerializer):
    years = YearSerializer(many=True, read_only=True)
    subject = SubjectWithExamSerializer(many=True, read_only=True)
    options = OptionSerializer(many=True, read_only=True)
    solution = SolutionSerializer(read_only=True)
    user_attempt = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "statement",
            "years",
            "subject",
            "is_active",
            "created_at",
            "options",
            "solution",
            "user_attempt",
        ]

    def get_user_attempt(self, obj):
        user = self.context.get("request").user
        attempt = Attempt.objects.filter(question=obj, user=user).first()
        if attempt:
            return AttemptSerializer(attempt).data
        return None


class ExamWithoutSubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        # fields = "__all__"
        exclude = ["subjects"]


# ---------------------------------------------------Analytics Section -----------------------------
class AnalyticsSerializer(serializers.ModelSerializer):
    years = YearSerializer(many=True, read_only=True)
    user_attempt = serializers.SerializerMethodField()
    # options = OptionCorrectIncorrectSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "years",
            "user_attempt",
            "chapter",
            "subject",
        ]

    def get_user_attempt(self, obj):
        user = self.context.get("request").user
        attempts = Attempt.objects.filter(question=obj, user=user).all()
        serialized_attempts = []
        for attempt in attempts:
            serialized_attempts.append(
                AttemptSerializerWithDetailedOptions(attempt).data
            )
        #     return AttemptSerializerWithDetailedOptions(attempt).data
        return serialized_attempts

    # ------------------------------------Study Material ---------------------------


class StudyMaterialSerializer(serializers.ModelSerializer):
    exam = ExamWithoutSubjectsSerializer(read_only=True)
    year = YearSerializer(read_only=True)
    subject = SubjectWithoutChaptersSerializer(read_only=True)

    class Meta:
        model = StudyMaterial
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):
    study_material = StudyMaterialSerializer(
        many=True, read_only=True, source="studymaterial_set"
    )

    class Meta:
        model = Topic
        fields = "__all__"


class DiamondSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diamond
        fields = "__all__"


# ------------------------------------Daily questions---------------------------
class DailyQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = DailyQuestion
        fields = "__all__"


class DailyQuestionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = ["question", "selected_option"]

    def create(self, validated_data):
        user = self.context["request"].user
        attempt, created = Attempt.objects.update_or_create(
            user=user,
            question=validated_data["question"],
            defaults={"selected_option": validated_data["selected_option"]},
        )
        return attempt


# ------------------------------------User Auth---------------------------


class UserEmailAuthSerializer(serializers.ModelSerializer):
    token_expiry = serializers.SerializerMethodField()
    otp_expiry = serializers.SerializerMethodField()

    class Meta:
        model = UserEmailAuth
        fields = [
            "token",
            "otp",
            "otp_created_at",
            "otp_expiry",
            "token_updated_at",
            "token_expiry",
        ]

    def get_token_expiry(self, obj):
        # Ensure the token_expiry is timezone aware
        token_expiry = obj.token_updated_at + timedelta(seconds=EMAIL_TOKEN_VALIDITY)
        return timezone.localtime(token_expiry)  # Convert to local timezone

    def get_otp_expiry(self, obj):
        # Ensure the otp_expiry is timezone aware
        otp_expiry = obj.otp_created_at + timedelta(seconds=OTP_VALIDITY)
        return timezone.localtime(otp_expiry)  # Convert to local timezone


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    userdetails = UserDetailsSerializer(
        read_only=True
    )  # Nested serializer for user details

    class Meta:
        model = UserProfile
        fields = ["email", "first_name", "last_name", "phone_number", "userdetails"]


class UpcomingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpcomingPlan
        fields = ["id", "content", "created_at", "updated_at"]
