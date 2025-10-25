from django.shortcuts import render
from django.http import JsonResponse
from incidents.models import Incident
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate, TruncHour
from datetime import timedelta
from django.utils import timezone

def analytics_dashboard(request):
    """Analytics and reporting dashboard"""
    return render(request, 'analytics/dashboard.html')

def get_analytics_data(request):
    """API endpoint for analytics data"""
    # Daily incident trends (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_trends = Incident.objects.filter(
        reported_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('reported_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Response time statistics
    resolved_incidents = Incident.objects.filter(
        status='RESOLVED',
        resolved_at__isnull=False
    )
    
    response_times = []
    for incident in resolved_incidents:
        if incident.dispatched_at:
            delta = incident.resolved_at - incident.dispatched_at
            response_times.append(delta.total_seconds() / 60)  # Convert to minutes
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Emergency type distribution
    type_distribution = list(Incident.objects.values('emergency_type').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    # Severity distribution
    severity_distribution = list(Incident.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    return JsonResponse({
        'daily_trends': list(daily_trends),
        'avg_response_time': round(avg_response_time, 2),
        'type_distribution': type_distribution,
        'severity_distribution': severity_distribution,
        'total_incidents': Incident.objects.count(),
        'resolved_count': resolved_incidents.count(),
    })
