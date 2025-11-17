from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import datetime


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
        ('electrician', 'Electrician'),
        ('storekeeper', 'Storekeeper'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='electrician')

    site_location = models.CharField(max_length=255, blank=True, null=True)  

    def __str__(self):
        return f"{self.username} ({self.role})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    ATTENDANCE_TYPE = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)

    total_hours = models.FloatField(null=True, blank=True)

    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE, default='present')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def hours_worked(self):
        if self.clock_in and self.clock_out:
            diff = self.clock_out - self.clock_in
            return round(diff.total_seconds() / 3600, 2)
        return None

    def map_link(self):
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return ""


    def __str__(self):
        return f"{self.user.username} | {self.date} | {self.status}"


class WorkReport(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ fixed

    def __str__(self):
        return f"{self.user.username} - {self.task_name} ({self.created_at.date()})"


class MaterialRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    # 🔹 Fixed the ForeignKey line
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50, null=True, blank=True) 
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='material_photos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} x {self.quantity} ({self.user.username})"