from django.db import models
from markdownx.models import MarkdownxField

class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = MarkdownxField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name
    
    
class Exam(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subjects = models.ManyToManyField('Subject', related_name='exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = MarkdownxField(blank=True)
    subjects = models.ManyToManyField(Subject, related_name='chapters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 
    
    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name


class StudyMaterial(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    topic = models.ManyToManyField(Topic, related_name='study_materials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.topic.name


class Year(models.Model):
    year = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.year


class Question(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    years = models.ManyToManyField(Year, related_name='questions')
    chapter = models.ManyToManyField(Chapter, related_name='questions')
    subject = models.ManyToManyField(Subject, related_name='questions')
    topic = models.ManyToManyField(Topic, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.id


class Option(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

class Solution(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    question = models.OneToOneField(Question, related_name='solution', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.statement[:50]

class DailyQuestion(models.Model):
    date = models.DateField(unique=True)
    question = models.ForeignKey(Question, related_name='daily_questions', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Daily Question for {self.date}"


class Attempt(models.Model):
    user = models.UUIDField(editable=False)
    questions = models.ManyToManyField(Question, related_name='attempts')
    options = models.ManyToManyField(Option, related_name='attempts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user} - Q{self.question.id}"
