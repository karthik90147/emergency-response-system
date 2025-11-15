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
from django.contrib import messages
from django.contrib.auth import logout 

# Initialize AI utilities
classifier = EmergencyClassifier()
detector = EmergencyImageDetector()

def welcome_screen(request):
    """New root view to ask user role and route them, forcing admin re-auth."""
    
    # --- Enforce Re-authentication for Staff Users ---
    if request.user.is_authenticated and request.user.is_staff:
        logout(request)
    
    return render(request, 'welcome.html')

def home(request):
    """Home page with emergency reporting form (now at /report/)"""
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
    
    # If type is 'NONE', it explicitly skips assignment
    if emergency_type == 'NONE':
        return []
        
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
        # Using the local or imported calculate_distance function
        distance = calculate_distance(
            latitude, longitude,
            responder.current_latitude, responder.current_longitude
        )
        responder_distances.append((responder, distance))
    
    # Sort by distance and get nearest
    responder_distances.sort(key=lambda x: x[1])
    nearest = responder_distances[:count]
    
    return [r[0] for r in nearest]

def send_agency_notification(incident):
    """Send email notification to the central agency (Hospital, Fire, Police)"""
    try:
        subject = f'🚨 Emergency Alert: {incident.get_emergency_type_display()} - {incident.incident_id}'
        
        # --- START: Fetch and Format Nearby Services (Conditional Logic Applied) ---
        nearby_hospitals = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Hospital', count=3)
        nearby_police = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Police Station', count=2)
        nearby_fire = find_nearest_emergency_services(incident.latitude, incident.longitude, category='Fire Station', count=2)
        
        nearby_services_text = "\nNearby Emergency Services:\n"
        incident_type = incident.emergency_type

        def format_service_section(title, services):
            text = ""
            if services:
                text += f"\n{title}:\n"
                for service in services:
                    text += f"- {service['name']} ({service['distance']} km)\n  {service['address']}\n"
            return text
            
        if incident_type != 'POLICE_ONLY_FOR_MEDICAL': 
             nearby_services_text += format_service_section("Hospitals", nearby_hospitals)

        if incident_type in ['ACCIDENT', 'CRIME', 'NATURAL', 'OTHER']:
            nearby_services_text += format_service_section("Police Stations", nearby_police)

        if incident_type in ['FIRE', 'NATURAL']:
            nearby_services_text += format_service_section("Fire Stations", nearby_fire)
            
        # --- END: Fetch and Format Nearby Services ---
        
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
        recipient_list = []
        
        # Define email aliases (MUST be configured in settings.py)
        POLICE_EMAIL = 'policehydresuce@gmail.com'
        HOSPITAL_EMAIL = 'nbk.hospitals@gmail.com'
        FIRE_EMAIL = 'firestation659@gmail.com'
        
        if incident.emergency_type == 'FIRE':
            recipient_list.append(FIRE_EMAIL)
            recipient_list.append(HOSPITAL_EMAIL) 
        elif incident.emergency_type == 'MEDICAL':
            recipient_list.append(HOSPITAL_EMAIL)
        elif incident.emergency_type == 'ACCIDENT':
            recipient_list.append(HOSPITAL_EMAIL)
            recipient_list.append(POLICE_EMAIL) 
        elif incident.emergency_type == 'CRIME':
            recipient_list.append(POLICE_EMAIL)
            recipient_list.append(HOSPITAL_EMAIL)
        elif incident.emergency_type == 'NATURAL':
            recipient_list.append(POLICE_EMAIL)
            recipient_list.append(HOSPITAL_EMAIL) 
        elif incident.emergency_type != 'NONE': # Default for OTHER, ensuring NONE is skipped
            recipient_list.append(POLICE_EMAIL)
        
        if not from_email or not recipient_list:
            print("Email configuration missing: DEFAULT_FROM_EMAIL or recipient list is empty")
            return False
            
        result = send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        if result > 0:
            print(f"Email notification sent successfully for incident {incident.incident_id} to {', '.join(recipient_list)}")
            return True
        else:
            print(f"Email sending failed for incident {incident.incident_id}: No emails were sent")
            return False
            
    except Exception as e:
        import traceback
        print(f"Agency Email sending failed for incident {incident.incident_id}: {str(e)}")
        print(traceback.format_exc())
        return False

def send_responder_assignment_notification(incident, responder):
    """Sends a personalized notification to the assigned responder unit."""
    try:
        subject = f'✅ New Incident Assignment: {incident.incident_id}'
        message = f"""
Dear {responder.name},

You have been assigned to a new incident.

Incident ID: {incident.incident_id}
Type: {incident.get_emergency_type_display()}
Severity: {incident.get_severity_display()}

Location:
Latitude: {incident.latitude}
Longitude: {incident.longitude}
Address: {incident.address or 'Not provided'}
Details: {incident.description}

Please proceed immediately. Your status has been set to BUSY.
"""
        from_email = settings.EMAIL_HOST_USER
        
        # Ensures the responder has an email before attempting to send
        if not responder.email:
            print(f"Skipping assignment email: Responder {responder.name} has no email address.")
            return

        send_mail(
            subject,
            message,
            from_email,
            [responder.email], # Sends directly to the responder's email address
            fail_silently=False,
        )
        print(f"Assignment email sent to Responder: {responder.name} ({responder.email})")

    except Exception as e:
        print(f"Error sending assignment email to Responder {responder.name}: {e}")

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
            
            # Check for missing location data
            if not latitude or not longitude:
                raise ValueError("Location coordinates (latitude and longitude) are required.")
                
            # Convert to float to ensure consistency with calculate_distance argument expectations
            try:
                float(latitude)
                float(longitude)
            except ValueError:
                raise ValueError("Invalid latitude or longitude value.")
            
            # Combine description and voice transcript
            full_text = f"{description} {voice_transcript}".strip()
            
            # AI Classification (First Pass)
            emergency_type, severity, confidence = classifier.classify_emergency(full_text)
            
            # --- START: NEW CHECK FOR NON-EMERGENCY REPORTS ---
            if confidence * 100 < 20: # 20% threshold
                emergency_type = 'NONE'
                severity = 'LOW'
                confidence = 0.01 
            # --- END: NEW CHECK ---
            
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
            
            # Handle image upload and safety check
            if 'image' in request.FILES:
                incident.image = request.FILES['image']
                incident.save()
                
                # --- START: IMAGE DETECTION FIX (Corrected Safety Logic) ---
                print("INFO: Media uploaded. Checking for classification override.")
                
                # Store the initial text-based classification for possible fallback
                initial_type = incident.emergency_type
                initial_severity = incident.severity
                
                try:
                    # 1. Object Detection and Fire Check
                    detection_log, detected_type = detector.detect_emergency_objects(incident.image.path) 
                    is_fire, fire_conf = detector.analyze_fire(incident.image.path)
                    
                    if is_fire:
                        # Safety Rule 1: If FIRE is confirmed, override to CRITICAL
                        incident.ai_detection_result = f"FIRE CONFIRMED: {fire_conf:.1f}% confidence. Triage enforced. | {detection_log}"
                        incident.emergency_type = 'FIRE'
                        incident.severity = 'CRITICAL'
                    elif detected_type != 'OTHER':
                        # Safety Rule 2: If ACCIDENT/MEDICAL objects detected, override TYPE and promote severity
                        # Only override TYPE if the text classification was NONE or OTHER
                        if initial_type in ['NONE', 'OTHER']:
                            incident.emergency_type = detected_type
                            incident.severity = 'HIGH' # Promote severity based on visual confirmation
                            incident.ai_detection_result = f"VISUAL CHECK: {detection_log}. Type promoted to {detected_type}."
                        else:
                            # If text classification was already good (e.g., MEDICAL), just log the detection
                            incident.ai_detection_result = f"VISUAL CHECK: {detection_log}. Text classification retained."
                        
                    incident.save()
                    
                except Exception as e:
                    # If ML scan fails entirely, log failure but retain the text classification results
                    print(f"ML Image scan failed/bypassed: {e}. Trusting text classification.")
                    
                # --- END: IMAGE DETECTION FIX ---

            # Find and assign nearest responders
            nearest_responders = find_nearest_responders(
                incident.latitude,
                incident.longitude,
                incident.emergency_type
            )
            
            # Initialize response status
            response_message = 'Report received. No immediate dispatch required.'
            
            if incident.emergency_type == 'NONE':
                 incident.status = 'CLOSED'
                 incident.save()
                 
                 return JsonResponse({
                     'success': True,
                     'incident_id': incident.incident_id,
                     'emergency_type': 'NON-EMERGENCY',
                     'severity': 'NONE',
                     'responders_assigned': 0,
                     'message': 'Report classified as non-emergency (Confidence too low). Dispatch aborted.'
                 })
            
            # Assign responders (Only if type is NOT NONE)
            assigned_responders = [] 
            if nearest_responders:
                for responder in nearest_responders:
                    IncidentAssignment.objects.create(
                        incident=incident,
                        responder=responder
                    )
                    responder.status = 'BUSY'
                    responder.save()
                    assigned_responders.append(responder) 

            
            # Update incident status and set final message
            if assigned_responders:
                incident.status = 'DISPATCHED'
                incident.dispatched_at = timezone.now()
                incident.save()
                # --- SUCCESS MESSAGE MODIFICATION ---
                response_message = 'Emergency reported successfully! Help is on the way.'
            else:
                # --- FAILURE MESSAGE MODIFICATION (for non-availability) ---
                incident.status = 'REPORTED' # Ensure status remains 'REPORTED' if not dispatched
                incident.save()
                response_message = f"Critical incident ({incident.get_emergency_type_display()}) reported. We have notified the control room and are mobilizing alternative resources **immediately**."
                
            # Send initial agency email notification
            send_agency_notification(incident) 
            
            # Send personalized notification to each assigned responder (only if dispatched)
            for responder in assigned_responders:
                send_responder_assignment_notification(incident, responder) 
            
            return JsonResponse({
                'success': True,
                'incident_id': incident.incident_id,
                'emergency_type': incident.get_emergency_type_display(),
                'severity': incident.get_severity_display(),
                'responders_assigned': len(assigned_responders), # Use len(assigned_responders) here
                'message': response_message
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
    """Real-time incident tracking page (Simplified Timeline)"""
    incident = get_object_or_404(Incident, incident_id=incident_id)
    
    return render(request, 'incidents/track_incident.html', {
        'incident': incident,
    })


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


def tracking_panel(request):
    """Public facing page with the tracking panel (renders home page with tracking focus)"""
    return render(request, 'incidents/home.html')
    
def track_incident_by_id(request, incident_id):
    """Helper view to redirect based on ID or show error"""
    try:
        Incident.objects.get(incident_id=incident_id)
        return redirect('incidents:track_incident', incident_id=incident_id)
    except Incident.DoesNotExist:
        return redirect('incidents:tracking_panel') 

def tracking_panel_submit(request):
    """Handles the form submission from the tracking panel"""
    if request.method == 'POST':
        incident_id = request.POST.get('incident_id', '').strip()
        if not incident_id:
            messages.error(request, 'Please enter a valid Incident ID.')
            return redirect('incidents:tracking_panel') 
            
        try:
            Incident.objects.get(incident_id=incident_id)
            return redirect('incidents:track_incident', incident_id=incident_id)
        except Incident.DoesNotExist:
            messages.error(request, f'Incident ID {incident_id} not found. Please check the ID and try again.')
            return redirect('incidents:tracking_panel')
    
    return redirect('incidents:tracking_panel')