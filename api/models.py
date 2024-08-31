from django.db import models
from markdownx.models import MarkdownxField

class Subject(models.Model):
    name = models.CharField(max_length=255)
    description = MarkdownxField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name
    
    
class Exam(models.Model):
    name = models.CharField(max_length=255)
    subjects = models.ManyToManyField('Subject', related_name='exams')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=255)
    description = MarkdownxField(blank=True)
    subjects = models.ManyToManyField(Subject, related_name='chapters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 
    
    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name


class StudyMaterial(models.Model):
    topic = models.ManyToManyField(Topic, related_name='study_materials')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.topic.name} - {self.reference.statement[:50]}"


class Year(models.Model):
    year = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.year


class Question(models.Model):
    statement = MarkdownxField()
    years = models.ManyToManyField(Year, related_name='questions')
    chapter = models.ManyToManyField(Chapter, related_name='questions')
    subject = models.ManyToManyField(Subject, related_name='questions')
    topic = models.ManyToManyField(Topic, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"Q{self.id}: {self.statement[:50]}"


class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    statement = MarkdownxField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.statement[:50]

class Solution(models.Model):
    question = models.OneToOneField(Question, related_name='solution', on_delete=models.CASCADE)
    statement = MarkdownxField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.statement[:50]

class Attempt(models.Model):
    user = models.UUIDField(editable=False)
    questions = models.ManyToManyField(Question, related_name='attempts')
    options = models.ManyToManyField(Option, related_name='attempts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user} - Q{self.question.id} - {self.option.statement[:50]}"
