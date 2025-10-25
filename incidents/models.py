from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Incident(models.Model):
    EMERGENCY_TYPES = [
        ('FIRE', 'Fire Emergency'),
        ('MEDICAL', 'Medical Emergency'),
        ('ACCIDENT', 'Road Accident'),
        ('CRIME', 'Crime/Violence'),
        ('NATURAL', 'Natural Disaster'),
        ('OTHER', 'Other Emergency'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('REPORTED', 'Reported'),
        ('DISPATCHED', 'Dispatched'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    # Basic Information
    incident_id = models.CharField(max_length=20, unique=True, editable=False)
    reporter_name = models.CharField(max_length=100, blank=True, null=True)
    reporter_phone = models.CharField(max_length=15, blank=True, null=True)
    reporter_email = models.EmailField(blank=True, null=True)
    
    # Emergency Details
    emergency_type = models.CharField(max_length=20, choices=EMERGENCY_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    description = models.TextField()
    voice_transcript = models.TextField(blank=True, null=True)
    
    # Location Information
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField(blank=True, null=True)
    
    # Media Files
    image = models.ImageField(upload_to='incident_images/', blank=True, null=True)
    ai_detection_result = models.TextField(blank=True, null=True)
    
    # Status and Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REPORTED')
    reported_at = models.DateTimeField(auto_now_add=True)
    dispatched_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    # AI Classification
    ai_confidence = models.FloatField(default=0.0)
    ai_classification = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['-reported_at']),
            models.Index(fields=['status']),
            models.Index(fields=['emergency_type']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.incident_id:
            # Generate unique incident ID
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.incident_id = f'INC-{timestamp}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.incident_id} - {self.get_emergency_type_display()}"
