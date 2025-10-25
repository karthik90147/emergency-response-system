from django.db import models
from django.contrib.auth.models import User

class Responder(models.Model):
    RESPONDER_TYPES = [
        ('AMBULANCE', 'Ambulance'),
        ('POLICE', 'Police'),
        ('FIRE', 'Fire Department'),
        ('RESCUE', 'Rescue Team'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('BUSY', 'Busy'),
        ('OFFLINE', 'Offline'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100)
    responder_type = models.CharField(max_length=20, choices=RESPONDER_TYPES)
    vehicle_number = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    
    # Location
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    is_active = models.BooleanField(default=True)
    
    # Statistics
    total_responses = models.IntegerField(default=0)
    successful_responses = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_responder_type_display()}"

class IncidentAssignment(models.Model):
    from incidents.models import Incident
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='assignments')
    responder = models.ForeignKey(Responder, on_delete=models.CASCADE, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['incident', 'responder']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.incident.incident_id} - {self.responder.name}"

class EmergencyService(models.Model):
    CATEGORY_CHOICES = [
        ('Hospital', 'Hospital'),
        ('Fire Station', 'Fire Station'),
        ('Police Station', 'Police Station'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    address = models.TextField()
    locality = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    source = models.URLField(blank=True, null=True)
    
    # Location coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.category}) - {self.locality}"
    
    def __str__(self):
        return f"{self.name} - {self.get_responder_type_display()}"

class IncidentAssignment(models.Model):
    from incidents.models import Incident
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='assignments')
    responder = models.ForeignKey(Responder, on_delete=models.CASCADE, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['incident', 'responder']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.incident.incident_id} - {self.responder.name}"
