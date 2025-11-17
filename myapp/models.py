from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, id_number, email, password=None, role='security', fullname="Unknown"):
        if not id_number:
            raise ValueError("Users must have an ID number")
        user = self.model(id_number=id_number, email=email, role=role, fullname=fullname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id_number, email, password=None, fullname="Administrator"):
        user = self.create_user(id_number=id_number, email=email, password=password, role='admin', fullname=fullname)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('security', 'Security Officer'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Administrator'),
    ]

    id_number = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=255, default="Unknown")
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'id_number'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.id_number} - {self.fullname} ({self.role})"


class Duty(models.Model):
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="duties"
    )
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    time_start = models.TimeField()
    time_end = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("completed", "Completed")],
        default="pending",
    )

    def __str__(self):
        return f"{self.title} - {self.staff.username}"


class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255, blank=True)  
    role = models.CharField(max_length=50, blank=True)      
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.fullname:
            self.fullname = self.user.fullname
        if not self.role:
            self.role = self.user.role
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fullname} ({self.role}) - {self.check_in.date()}"
