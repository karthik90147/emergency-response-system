from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Incident
from responders.models import Responder, IncidentAssignment
from django.utils import timezone

def get_active_incidents(request):
    """API endpoint for active incidents"""
    incidents = Incident.objects.filter(
        status__in=['REPORTED', 'DISPATCHED', 'IN_PROGRESS']
    ).values(
        'incident_id',
        'emergency_type',
        'severity',
        'latitude',
        'longitude',
        'status',
        'reported_at',
        'description'
    )
    
    return JsonResponse({
        'incidents': list(incidents),
        'count': incidents.count()
    })

def get_incident_status(request, incident_id):
    """Get real-time status of specific incident"""
    try:
        incident = Incident.objects.get(incident_id=incident_id)
        assignments = IncidentAssignment.objects.filter(
            incident=incident
        ).select_related('responder')
        
        responders_data = []
        for assignment in assignments:
            responders_data.append({
                'name': assignment.responder.name,
                'type': assignment.responder.get_responder_type_display(),
                'vehicle': assignment.responder.vehicle_number,
                'status': assignment.responder.status,
                'latitude': float(assignment.responder.current_latitude) if assignment.responder.current_latitude else None,
                'longitude': float(assignment.responder.current_longitude) if assignment.responder.current_longitude else None,
            })
        
        return JsonResponse({
            'incident_id': incident.incident_id,
            'status': incident.status,
            'emergency_type': incident.get_emergency_type_display(),
            'severity': incident.severity,
            'responders': responders_data,
            'reported_at': incident.reported_at.isoformat(),
        })
    except Incident.DoesNotExist:
        return JsonResponse({'error': 'Incident not found'}, status=404)

def get_available_responders(request):
    """Get list of available responders"""
    responders = Responder.objects.filter(
        status='AVAILABLE',
        is_active=True
    ).values(
        'id',
        'name',
        'responder_type',
        'vehicle_number',
        'current_latitude',
        'current_longitude'
    )
    
    return JsonResponse({
        'responders': list(responders),
        'count': responders.count()
    })

@csrf_exempt
def update_incident_status(request, incident_id):
    """Update incident status"""
    if request.method == 'POST':
        try:
            incident = Incident.objects.get(incident_id=incident_id)
            new_status = request.POST.get('status')
            
            if new_status in dict(Incident.STATUS_CHOICES):
                incident.status = new_status
                
                if new_status == 'RESOLVED' and not incident.resolved_at:
                    incident.resolved_at = timezone.now()
                
                incident.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Status updated successfully',
                    'new_status': incident.get_status_display()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid status'
                }, status=400)
        except Incident.DoesNotExist:
            return JsonResponse({'error': 'Incident not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
