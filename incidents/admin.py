from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['incident_id', 'emergency_type', 'severity', 'status', 'reported_at']
    list_filter = ['emergency_type', 'severity', 'status', 'reported_at']
    search_fields = ['incident_id', 'description', 'reporter_name']
    readonly_fields = ['incident_id', 'reported_at', 'ai_confidence', 'ai_classification']
    
    fieldsets = (
        ('Incident Information', {
            'fields': ('incident_id', 'emergency_type', 'severity', 'description', 'status')
        }),
        ('Reporter Details', {
            'fields': ('reporter_name', 'reporter_phone', 'reporter_email')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('AI Analysis', {
            'fields': ('ai_classification', 'ai_confidence', 'ai_detection_result', 'voice_transcript')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('reported_at', 'dispatched_at', 'resolved_at')
        }),
    )
