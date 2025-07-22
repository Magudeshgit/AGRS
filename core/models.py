from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


# AUTH FRAME
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('parent', 'Parent'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    department_name = models.CharField(max_length=100, blank=True, null=True)
    user_score = models.IntegerField(default=50)  # Start with neutral score
    contact = models.CharField(max_length=13)
    
class department(models.Model):
    name = models.CharField(max_length=100)
    user_authority = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    superior = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    
    is_academic = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


# APP FRAME
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    department = models.ForeignKey(department, on_delete=models.CASCADE)
    
    incident_timestamp = models.DateTimeField()
    evidence = models.FileField(upload_to='evidence/', null=True, blank=True)
    
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    used_for_training = models.BooleanField(default=False)
    priority_score = models.FloatField(default=0.0, blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.department}"

class Response(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    support_file = models.FileField(upload_to='supportfiles/', null=True, blank=True)
    
    
    response_timestamp = models.DateTimeField(auto_now=True)
    department = models.ForeignKey(department, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class ComplaintAssignment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    department = models.ForeignKey(department, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField()
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.complaint + " - " + self.deadline
    
    
    


# class ComplaintTrail(models.Model):
#     complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
#     changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#     old_status = models.CharField(max_length=20)
#     new_status = models.CharField(max_length=20)
#     timestamp = models.DateTimeField(auto_now_add=True)


class LLMTrainingSample(models.Model):
    complaint_text = models.TextField()
    department = models.CharField(max_length=50)


class VoiceInput(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    audio_file = models.FileField(upload_to='voice/')
    transcribed_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EmailComplaint(models.Model):
    sender = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
    complaint_linked = models.ForeignKey(Complaint, null=True, blank=True, on_delete=models.SET_NULL)


class NotificationLog(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=50)  # email, sms, etc.
    status = models.CharField(max_length=20)        # sent, failed
    timestamp = models.DateTimeField(auto_now_add=True)

class WhatsAppLog(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=True, blank=True)
    to_number = models.CharField(max_length=20)
    message_text = models.TextField()
    status = models.CharField(max_length=10)  # sent / failed
    recipient_role = models.CharField(max_length=10)  # user / department
    timestamp = models.DateTimeField(auto_now_add=True)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.to_number} | {self.status} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

