from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        ORGANIZER = "organizer", "Organizer"
        ADMIN = "admin", "Administrator"

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    student_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^\+?[0-9]{9,15}$", "Enter a valid phone number.")],
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone_number", "username"]

    def __str__(self):
        return self.full_name or self.email
