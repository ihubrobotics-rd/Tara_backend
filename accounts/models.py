from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    phone_number = models.BigIntegerField(null=True, blank=True)
    profile_pic = models.FileField(upload_to='profile_pics/', null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')
    otp=models.IntegerField(null=True,blank=True)
    is_approved = models.BooleanField(default=False)


    