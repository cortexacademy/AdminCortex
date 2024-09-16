import binascii
import os

from django.db import models
from markdownx.models import MarkdownxField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone as dtime
from admin_panel.settings import EMAIL_TOKEN_VALIDITY, OTP_VALIDITY
from .manager import UserManager
from .utils import custom_upload_to
from django.core.exceptions import ValidationError


class UserProfile(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    def __str__(self):
        return self.email


class UserEmailAuth(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    otp_created_at = models.DateTimeField()
    token_updated_at = models.DateTimeField()
    token = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.otp_created_at:
            self.otp_created_at = dtime.now()

        if not self.token_updated_at:
            self.token_updated_at = dtime.now()
        if not self.token:
            self.token = self.generate_key()
        # create a random 6 digit OTP
        self.otp = (self.generate_key()[:6]).upper()
        return super().save(*args, **kwargs)

    def check_token(self):
        if (dtime.now() - self.token_updated_at).seconds > EMAIL_TOKEN_VALIDITY:
            raise ValidationError("Token expired")
        else:
            return True

    def refresh_otp(self):
        self.otp = (self.generate_key()[:6]).upper()
        self.otp_created_at = dtime.now()
        self.save()

    def verify_otp(self, otp):
        self.check_token()
        if self.otp == otp:
            if (dtime.now() - self.otp_created_at).seconds > OTP_VALIDITY:
                raise ValidationError("OTP expired")
            self.is_verified = True
            self.save()
            self.refresh_object()
            return True

        return False

    def refresh_token(self):
        self.token = self.generate_key()
        self.token_updated_at = dtime.now()
        self.save()

    def refresh_object(self):
        self.refresh_otp()
        self.refresh_token()

    def send_otp(self):
        return True

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


class Image(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=custom_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url
        return None


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = MarkdownxField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} {self.name}"


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
        return f"{self.id} {self.name}"


class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} {self.name}"


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
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Option id: {self.id}"


class Solution(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    question = models.OneToOneField(
        Question, on_delete=models.CASCADE, related_name="solution"
    )
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
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user.email} - Q{self.question.id} - Option {self.selected_option.id}"
