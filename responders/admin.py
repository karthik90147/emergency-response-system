from django.contrib import admin
from .models import Responder, IncidentAssignment

@admin.register(Responder)
class ResponderAdmin(admin.ModelAdmin):
    list_display = ['name', 'responder_type', 'status', 'vehicle_number', 'contact_number']
    list_filter = ['responder_type', 'status', 'is_active']
    search_fields = ['name', 'vehicle_number', 'contact_number']

@admin.register(IncidentAssignment)
class IncidentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['incident', 'responder', 'assigned_at', 'accepted_at', 'completed_at']
    list_filter = ['assigned_at']
    search_fields = ['incident__incident_id', 'responder__name']
