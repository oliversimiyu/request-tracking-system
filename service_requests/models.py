from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('password_reset', 'Password Reset'),
        ('software_installation', 'Software Installation'),
        ('hardware_issue', 'Hardware Issue'),
        ('printer_issue', 'Printer Issue'),
        ('network_issue', 'Network Issue'),
        ('account_access', 'Account Access'),
        ('other', 'Other'),
    ]
    
    requester_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.requester_name} - {self.get_category_display()} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Automation: Set default status to 'pending' if not set
        if not self.status:
            self.status = 'pending'
        super().save(*args, **kwargs)


class Department(models.Model):
    """Model to store department data from external API"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    manager = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
