from django.urls import path
from . import views, api_views

app_name = 'incidents'

urlpatterns = [
    # Root URL points to the welcome screen
    path('', views.welcome_screen, name='welcome'), 
    
    # Report Form page (GET request to render template)
    path('report/', views.home, name='home'),
    
    # Report Submission Endpoint (POST request from the form)
    path('report/submit/', views.report_emergency, name='report_emergency'), # <--- FIX: Added missing endpoint
    
    path('incident/<str:incident_id>/', views.incident_detail, name='incident_detail'),
    path('track/<str:incident_id>/', views.track_incident, name='track_incident'),
    
    # New public-facing tracking panel URLs
    path('track-panel/', views.tracking_panel, name='tracking_panel'), 
    path('track-panel/submit/', views.tracking_panel_submit, name='tracking_panel_submit'), 
    path('track-live/<str:incident_id>/', views.track_incident_by_id, name='track_incident_by_id'), 
    
    # API endpoints
    path('api/active/', api_views.get_active_incidents, name='api_active_incidents'),
    path('api/incident/<str:incident_id>/', api_views.get_incident_status, name='api_incident_status'),
    path('api/responders/', api_views.get_available_responders, name='api_available_responders'),
    path('incident/<str:incident_id>/update-status/', views.update_incident_status_view, name='update_status'),
]