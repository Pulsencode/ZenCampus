from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.db import models
from datetime import datetime
import random


class User(AbstractUser):
    GENDER_CHOICES = [("MAL", "Male"), ("FEM", "Female"), ("OTH", "Other")]
    registration_id = models.CharField(max_length=10, unique=True, editable=False)
    phone_number = models.CharField(max_length=15, null=True)
    address = models.TextField(null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=3, choices=GENDER_CHOICES, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture/", null=True, blank=True
    )
    emergency_contact = models.CharField(max_length=15, blank=True)
    joining_date = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(
            ("pbkdf2_sha256$", "bcrypt$", "argon2")
        ):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


    def generate_registration_id(self, prefix):
        year = datetime.now().year
        while True:
            random_number = random.randint(1000, 9999)
            registration_id = f"{prefix}{year}{random_number}"
            if not User.objects.filter(registration_id=registration_id).exists():
                return registration_id

    def __str__(self):
        return f"{self.username} - {self.registration_id}"


class Admin(User):
    department = models.ForeignKey(
        "management.Department", on_delete=models.SET_NULL, null=True
    )
    qualification = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admin"

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = self.generate_registration_id(prefix="ADM")
        super().save(*args, **kwargs)


class Staff(User):
    department = models.ForeignKey(
        "management.Department", on_delete=models.SET_NULL, null=True
    )
    designation = models.CharField(max_length=50)
    qualification = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = self.generate_registration_id(prefix="STF")
        super().save(*args, **kwargs)


class Librarian(User):
    qualification = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Librarian"
        verbose_name_plural = "Librarians"
        permissions = [
            ("view_book", "Can view book"),
            ("add_book", "Can add book"),
            ("change_book", "Can change book"),
            ("delete_book", "Can delete book"),
            ("add_libraryrecord", "Can add library record"),
            ("view_libraryrecord", "Can view library record"),
            ("change_libraryrecord", "Can change library record"),
            ("delete_libraryrecord", "Can delete library record"),
        ]

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = self.generate_registration_id(prefix="LIB")
        super().save(*args, **kwargs)


class Student(User):
    grade = models.ForeignKey("management.Grade", on_delete=models.PROTECT)
    admission_date = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_contact_number = models.CharField(max_length=15)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Student"

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = self.generate_registration_id(prefix="STU")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.grade}"
