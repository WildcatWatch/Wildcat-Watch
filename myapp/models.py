from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('security', 'Security Officer'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    fullname = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    id_no = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.fullname} ({self.role})"
