from rest_framework import serializers
from .models import *

# ---------------------------------------------------For Subject/Chapter serializer----------------------

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        exclude =['subjects']


class SubjectSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True, source='chapter_set')

    class Meta:
        model = Subject
        fields = '__all__'


# ---------------------------------------------------For question serializer----------------------
class YearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = '__all__'


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution 
        fields = '__all__'
                


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = '__all__'
        # fields = ['question', 'selected_option']
    
    def create(self, validated_data):
        user = self.context['request'].user
        attempt = Attempt.objects.create(user=user, **validated_data)
        return attempt

class QuestionSerializer(serializers.ModelSerializer):
    years = YearSerializer(many=True, read_only=True)
    options = OptionSerializer(many=True, read_only=True, source='option_set') 
    solution = SolutionSerializer(read_only=True)
    user_attempt = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'statement', 'years', 'is_active', 'created_at', 'options', 'solution', 'user_attempt']

    def get_user_attempt(self, obj):
        user = self.context.get('request').user
        attempt = Attempt.objects.filter(question=obj, user=user).first()
        if attempt:
            return AttemptSerializer(attempt).data
        return None


# ---------------------------------------------------PYQ section-----------------------------

class SubjectWithoutChaptersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    subjects = SubjectWithoutChaptersSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'
        # fields = ['id', 'name', 'subjects', 'created_at', 'updated_at', 'is_active']


class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = ['id', 'statement', 'created_at', 'updated_at']


class TopicSerializer(serializers.ModelSerializer):
    study_material = StudyMaterialSerializer(many=True, read_only=True, source='studymaterial_set')

    class Meta:
        model = Topic
        fields = '__all__'
        

# ------------------------------------Daily questions---------------------------
class DailyQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    class Meta:
        model = DailyQuestion
        fields = '__all__'


class DailyQuestionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = ['question', 'selected_option']

    def create(self, validated_data):
        user = self.context['request'].user
        attempt, created = Attempt.objects.update_or_create(
            user=user,
            question=validated_data['question'],
            defaults={'selected_option': validated_data['selected_option']}
        )
        return attempt
