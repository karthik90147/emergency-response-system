from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Incident
from responders.models import Responder, IncidentAssignment
from responders.utils import find_nearest_emergency_services
from .utils.ai_classifier import EmergencyClassifier
from .utils.image_detector import EmergencyImageDetector
from math import radians, sin, cos, sqrt, atan2
import json

# Initialize AI utilities
classifier = EmergencyClassifier()
detector = EmergencyImageDetector()

def home(request):
    """Home page with emergency reporting form"""
    return render(request, 'incidents/home.html')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def find_nearest_responders(latitude, longitude, emergency_type, count=3):
    """Find nearest available responders"""
    # Map emergency types to responder types
    type_mapping = {
        'FIRE': 'FIRE',
        'MEDICAL': 'AMBULANCE',
        'ACCIDENT': 'AMBULANCE',
        'CRIME': 'POLICE',
        'NATURAL': 'RESCUE',
    }
    
    responder_type = type_mapping.get(emergency_type, 'AMBULANCE')
    
    # Get available responders
    available_responders = Responder.objects.filter(
        responder_type=responder_type,
        status='AVAILABLE',
        is_active=True
    ).exclude(current_latitude__isnull=True)
    
    # Calculate distances
    responder_distances = []
    for responder in available_responders:
        distance = calculate_distance(
            latitude, longitude,
            responder.current_latitude, responder.current_longitude
        )
        responder_distances.append((responder, distance))
    
    # Sort by distance and get nearest
    responder_distances.sort(key=lambda x: x[1])
    nearest = responder_distances[:count]
    
    return [r[0] for r in nearest]

def send_emergency_notification(incident):
    """Send email notification for new emergency"""
    try:
        subject = f'🚨 Emergency Alert: {incident.get_emergency_type_display()} - {incident.incident_id}'
        
        # Find nearby emergency services
        nearby_hospitals = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Hospital', count=3)
        nearby_police = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Police Station', count=2)
        nearby_fire = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Fire Station', count=2)
        
        # Format nearby services for email
        nearby_services_text = "\nNearby Emergency Services:\n"
        
        if nearby_hospitals:
            nearby_services_text += "\nHospitals:\n"
            for hospital in nearby_hospitals:
                nearby_services_text += f"- {hospital['name']} ({hospital['distance']} km)\n  {hospital['address']}\n"
        
        if nearby_police:
            nearby_services_text += "\nPolice Stations:\n"
            for station in nearby_police:
                nearby_services_text += f"- {station['name']} ({station['distance']} km)\n  {station['address']}\n"
        
        if nearby_fire:
            nearby_services_text += "\nFire Stations:\n"
            for station in nearby_fire:
                nearby_services_text += f"- {station['name']} ({station['distance']} km)\n  {station['address']}\n"
        
        message = f"""
        New Emergency Reported!
        
        Incident ID: {incident.incident_id}
        Type: {incident.get_emergency_type_display()}
        Severity: {incident.get_severity_display()}
        
        Description: {incident.description}
        
        Location:
        Latitude: {incident.latitude}
        Longitude: {incident.longitude}
        Address: {incident.address or 'Not provided'}
        
        Reporter: {incident.reporter_name or 'Anonymous'}
        Contact: {incident.reporter_phone or 'Not provided'}
        
        AI Classification: {incident.ai_classification or 'Pending'}
        AI Confidence: {incident.ai_confidence}%
        
        Time Reported: {incident.reported_at.strftime('%Y-%m-%d %H:%M:%S')}
        
        Status: {incident.get_status_display()}
        {nearby_services_text}
        --- 
        This is an automated emergency alert.
        Please respond immediately.
        """
        
        # Ensure we have valid email settings
        from_email = settings.EMAIL_HOST_USER
        
        # Determine recipient email based on emergency type
        if incident.emergency_type == 'FIRE':
            to_email = 'firestation659@gmail.com'
        elif incident.emergency_type in ['MEDICAL', 'ACCIDENT']:
            to_email = 'nbk.hospitals@gmail.com'
        else:  # CRIME, NATURAL, OTHER
            to_email = 'policehydresuce@gmail.com'
        
        if not from_email or not to_email:
            print("Email configuration missing: DEFAULT_FROM_EMAIL or recipient email not set")
            return False
            
        # Send the email with detailed error handling
        result = send_mail(
            subject,
            message,
            from_email,
            [to_email],
            fail_silently=False,
        )
        
        # Check if email was sent successfully (send_mail returns the number of successfully sent messages)
        if result > 0:
            print(f"Email notification sent successfully for incident {incident.incident_id} to {to_email}")
            return True
        else:
            print(f"Email sending failed for incident {incident.incident_id}: No emails were sent")
            return False
            
    except Exception as e:
        import traceback
        print(f"Email sending failed for incident {incident.incident_id}: {str(e)}")
        print(traceback.format_exc())
        return False

@csrf_exempt
def report_emergency(request):
    """Handle emergency report submission"""
    if request.method == 'POST':
        try:
            # Get form data
            description = request.POST.get('description', '')
            voice_transcript = request.POST.get('voice_transcript', '')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            address = request.POST.get('address', '')
            reporter_name = request.POST.get('reporter_name', '')
            reporter_phone = request.POST.get('reporter_phone', '')
            reporter_email = request.POST.get('reporter_email', '')
            
            # Combine description and voice transcript
            full_text = f"{description} {voice_transcript}".strip()
            
            # AI Classification
            emergency_type, severity, confidence = classifier.classify_emergency(full_text)
            
            # Create incident
            incident = Incident.objects.create(
                reporter_name=reporter_name,
                reporter_phone=reporter_phone,
                reporter_email=reporter_email,
                description=description,
                voice_transcript=voice_transcript,
                latitude=latitude,
                longitude=longitude,
                address=address,
                emergency_type=emergency_type,
                severity=severity,
                ai_confidence=confidence * 100,
                ai_classification=f"{emergency_type} - {severity}",
                status='REPORTED'
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                incident.image = request.FILES['image']
                incident.save()
                
                # Run image detection
                try:
                    detection_result = detector.detect_emergency_objects(incident.image.path)
                    is_fire, fire_conf = detector.analyze_fire(incident.image.path)
                    
                    if is_fire:
                        detection_result += f" | Fire detected ({fire_conf:.1f}% confidence)"
                        if incident.emergency_type != 'FIRE':
                            incident.emergency_type = 'FIRE'
                            incident.severity = 'CRITICAL'
                    
                    incident.ai_detection_result = detection_result
                    incident.save()
                except Exception as e:
                    print(f"Image detection error: {e}")
            
            # Find and assign nearest responders
            nearest_responders = find_nearest_responders(
                incident.latitude,
                incident.longitude,
                incident.emergency_type
            )
            
            # Assign responders
            for responder in nearest_responders:
                IncidentAssignment.objects.create(
                    incident=incident,
                    responder=responder
                )
                responder.status = 'BUSY'
                responder.save()
            
            # Update incident status
            if nearest_responders:
                incident.status = 'DISPATCHED'
                incident.dispatched_at = timezone.now()
                incident.save()
            
            # Send email notification
            send_emergency_notification(incident)
            
            return JsonResponse({
                'success': True,
                'incident_id': incident.incident_id,
                'emergency_type': incident.get_emergency_type_display(),
                'severity': incident.get_severity_display(),
                'responders_assigned': len(nearest_responders),
                'message': 'Emergency reported successfully! Help is on the way.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def incident_detail(request, incident_id):
    """View incident details"""
    incident = get_object_or_404(Incident, incident_id=incident_id)
    assignments = incident.assignments.select_related('responder').all()
    
    # Find nearby emergency services
    nearby_hospitals = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Hospital', count=3)
    nearby_police = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Police Station', count=2)
    nearby_fire = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Fire Station', count=2)
    
    context = {
        'incident': incident,
        'assignments': assignments,
        'nearby_hospitals': nearby_hospitals,
        'nearby_police': nearby_police,
        'nearby_fire': nearby_fire,
    }
    return render(request, 'incidents/incident_detail.html', context)

def track_incident(request, incident_id):
    """Real-time incident tracking page"""
    incident = get_object_or_404(Incident, incident_id=incident_id)
    
    # Find nearby emergency services
    nearby_hospitals = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Hospital', count=3)
    nearby_police = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Police Station', count=2)
    nearby_fire = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Fire Station', count=2)
    
    return render(request, 'incidents/track_incident.html', {
        'incident': incident,
        'nearby_hospitals': nearby_hospitals,
        'nearby_police': nearby_police,
        'nearby_fire': nearby_fire
    })


# Add this to the existing incidents/views.py

from django.shortcuts import redirect
from django.contrib import messages

def update_incident_status_view(request, incident_id):
    """Handle status updates from incident detail page"""
    if request.method == 'POST':
        incident = get_object_or_404(Incident, incident_id=incident_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Incident.STATUS_CHOICES):
            incident.status = new_status
            
            if new_status == 'RESOLVED' and not incident.resolved_at:
                incident.resolved_at = timezone.now()
                
                # Mark responders as available
                for assignment in incident.assignments.all():
                    assignment.responder.status = 'AVAILABLE'
                    assignment.responder.save()
            
            incident.save()
            messages.success(request, f'Incident status updated to {incident.get_status_display()}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('incidents:incident_detail', incident_id=incident_id)
