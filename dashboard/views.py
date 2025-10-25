from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from incidents.models import Incident
from responders.models import Responder, IncidentAssignment
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta


def control_room_dashboard(request):
    """Main control room dashboard"""
    # Get recent incidents
    recent_incidents = Incident.objects.all()[:20]
    
    # Get active incidents
    active_incidents = Incident.objects.filter(
        status__in=['REPORTED', 'DISPATCHED', 'IN_PROGRESS']
    )
    
    # Statistics
    total_incidents = Incident.objects.count()
    resolved_incidents = Incident.objects.filter(status='RESOLVED').count()
    pending_incidents = Incident.objects.filter(
        status__in=['REPORTED', 'DISPATCHED', 'IN_PROGRESS']
    ).count()
    
    # Emergency type breakdown
    type_breakdown = Incident.objects.values('emergency_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Severity breakdown
    severity_breakdown = Incident.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Available responders
    available_responders = Responder.objects.filter(
        status='AVAILABLE',
        is_active=True
    )
    
    # Format active incidents for map display
    active_incidents_list = []
    for incident in active_incidents:
        try:
            # Convert latitude and longitude to float, handling potential errors
            lat = float(incident.latitude) if incident.latitude else 0
            lng = float(incident.longitude) if incident.longitude else 0
            
            active_incidents_list.append({
                'incident_id': incident.incident_id,
                'latitude': lat,
                'longitude': lng,
                'emergency_type': incident.get_emergency_type_display(),
                'severity': incident.get_severity_display(),
                'status': incident.get_status_display()
            })
        except (ValueError, TypeError, AttributeError):
            # Skip incidents with invalid coordinates
            continue
    
    import json
    active_incidents_json = json.dumps(active_incidents_list)
    
    context = {
        'recent_incidents': recent_incidents,
        'active_incidents': active_incidents,
        'active_incidents_json': active_incidents_json,
        'total_incidents': total_incidents,
        'resolved_incidents': resolved_incidents,
        'pending_incidents': pending_incidents,
        'type_breakdown': type_breakdown,
        'severity_breakdown': severity_breakdown,
        'available_responders': available_responders,
    }
    
    return render(request, 'dashboard/control_room.html', context)
