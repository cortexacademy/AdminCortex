from django.db import models
from markdownx.models import MarkdownxField
from django.contrib.auth.models import AbstractUser
from .manager import UserManager


class UserProfile(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    def __str__(self):
        return self.email


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
    subjects = models.ManyToManyField("Subject")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Chapter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = MarkdownxField(blank=True)
    subjects = models.ManyToManyField(Subject)
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
    topic = models.ManyToManyField(Topic)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"studymaterial id: {self.id}"


class Year(models.Model):
    year = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.year


class Question(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    years = models.ManyToManyField(Year)
    chapter = models.ManyToManyField(Chapter)
    subject = models.ManyToManyField(Subject)
    topic = models.ManyToManyField(Topic)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Question id: {self.id}"


class Option(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Option id: {self.id}"


class Solution(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.statement[:50]


class DailyQuestion(models.Model):
    date = models.DateField(unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Daily Question for {self.date}"


class Attempt(models.Model):
    user = models.UUIDField(editable=False)
    questions = models.ManyToManyField(Question)
    options = models.ManyToManyField(Option)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user} - Q{self.question.id}"
