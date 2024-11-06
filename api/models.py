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
from django.db.models.signals import post_delete
from django.dispatch import receiver


class UserProfile(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    def __str__(self):
        return self.email


def validate_batch_year(value):
    valid_choices = [choice[0] for choice in UserDetails.ProfessionalYear.choices]
    print("HEREE", value, valid_choices)
    if value not in valid_choices:
        raise ValidationError(
            ("%(value)s is not a valid choice for batch_year."),
            params={"value": value},
        )


class UserDetails(models.Model):
    user = models.OneToOneField(
        UserProfile, blank=False, null=False, on_delete=models.CASCADE
    )
    # address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    native_state = models.CharField(max_length=255, null=True, blank=True)
    college_state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=8, null=True, blank=True)
    college_name = models.CharField(max_length=500, null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)

    class ProfessionalYear(models.TextChoices):
        FIRST_PROFF = "1st Proff"
        SECOND_PROFF = "2nd Proff"
        THIRD_PROFF_PART_1 = "3rd Proff - Part 1"
        THIRD_PROFF_PART_2 = "3rd Proff - Part 2"
        INTERN = "Intern"
        POST_INTERN = "Post Intern"
        OTHER = "Other"

    batch_year = models.CharField(
        max_length=20,
        choices=ProfessionalYear.choices,
        default=ProfessionalYear.OTHER,
        null=True,
        blank=True,
        validators=[validate_batch_year],  # Add custom validator here
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    newsletter = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        # Run full_clean to enforce all validators, including custom ones
        self.full_clean()
        super().save(*args, **kwargs)


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
        self.otp = self.generate_numeric_otp()
        return super().save(*args, **kwargs)

    def check_token(self):
        if (dtime.now() - self.token_updated_at).seconds > EMAIL_TOKEN_VALIDITY:
            raise ValidationError("Token expired")
        else:
            return True

    def refresh_otp(self):
        self.otp = self.generate_numeric_otp()
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

    @staticmethod
    def generate_numeric_otp():
        # Generate a 6-digit numeric OTP
        return f"{int.from_bytes(os.urandom(3), 'big') % 1000000:06d}"

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
    imageURL = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} {self.name}"


class Exam(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subjects = models.ManyToManyField(Subject)
    imageURL = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Chapter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = MarkdownxField(blank=True)
    imageURL = models.URLField(max_length=500, blank=True, null=True)
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


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} {self.name}"


class Year(models.Model):
    year = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.year


class StudyMaterial(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    year = models.ForeignKey(Year, null=True, on_delete=models.SET_NULL)
    subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"studymaterial id: {self.id}"


class Question(models.Model):
    statement = MarkdownxField(null=False, blank=False)
    years = models.ManyToManyField(Year, blank=True)
    chapter = models.ManyToManyField(Chapter, blank=True)
    subject = models.ManyToManyField(Subject, blank=True)
    topic = models.ManyToManyField(Topic, blank=True)
    tag = models.ManyToManyField(Tag, blank=True)
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
    selected_option = models.ManyToManyField(Option)
    is_first = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user.email} - Q{self.question.id}"


@receiver(post_delete, sender=Attempt)
def clear_selected_options(sender, instance, **kwargs):
    instance.selected_option.clear()


class Diamond(models.Model):
    name = models.CharField(max_length=255, unique=True)
    statement = MarkdownxField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RecentUpdate(models.Model):
    content = MarkdownxField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Update {self.id}"


class UpcomingPlan(models.Model):
    content = MarkdownxField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Upcoming Plan {self.id}"
