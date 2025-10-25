from django.urls import path
from . import views, api_views

app_name = 'incidents'

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report_emergency, name='report_emergency'),
    path('incident/<str:incident_id>/', views.incident_detail, name='incident_detail'),
    path('track/<str:incident_id>/', views.track_incident, name='track_incident'),
    
    # API endpoints
    path('api/active/', api_views.get_active_incidents, name='api_active_incidents'),
    path('api/incident/<str:incident_id>/', api_views.get_incident_status, name='api_incident_status'),
    path('api/responders/', api_views.get_available_responders, name='api_available_responders'),
    # path('api/incident/<str:incident_id>/update/', api_views.update_incident_status, name='api_update_status'),

    # Add to existing urlpatterns
    path('incident/<str:incident_id>/update-status/', views.update_incident_status_view, name='update_status'),

]
