from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, id_number, email, password=None, role='security', fullname=None):
        if not id_number:
            raise ValueError("Users must have an ID number")
        if not fullname:
            raise ValueError("Full name is required")
        
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
        ('security', 'Security Guard'),
        ('janitor', 'Janitor'),
        ('admin', 'Administrator'),
    ]

    id_number = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'id_number'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.id_number} - {self.fullname} ({self.role})"
    
class AdminAccessKey(models.Model):
    key = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def set_key(self, raw_key):
        self.key = make_password(raw_key)

    def verify_key(self, raw_key):
        return check_password(raw_key, self.key)

    def __str__(self):
        return f"Admin Access Key (used: {self.used})"

class Duty(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("missed", "Missed"), 
    ]

    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="duties"
    )
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    def __str__(self):
        return f"{self.title} - {self.staff.id_number}"

class Attendance(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    assigned_duty = models.ForeignKey(
        "Duty", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="attendance_records"
    )

    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        duty_name = f" - {self.assigned_duty.title}" if self.assigned_duty else ""
        return f"{self.user.fullname} ({self.user.role}){duty_name} - {self.check_in}"

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    
    related_duty = models.ForeignKey(
        'Duty', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.id_number} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']


class AdminProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='admin_profile'
    )
    fullname = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    blood_type = models.TextField(blank=True, null=True)
    nationality = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    emergency_contact = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    work_schedule = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullname or f"AdminProfile(user={getattr(self.user, 'id', 'unknown')})"

    class Meta:
        db_table = "admin_profiles"
        # set managed=True if you want Django to manage migrations and create/alter the table
        managed = False