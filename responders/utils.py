from math import radians, sin, cos, sqrt, atan2
from .models import EmergencyService

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

def find_nearest_emergency_services(latitude, longitude, category=None, count=3):
    """
    Find nearest emergency services based on user location
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        category: Optional filter for service category ('Hospital', 'Fire Station', 'Police Station')
        count: Number of services to return (default 3)
        
    Returns:
        List of nearest emergency services with distance information
    """
    # Get emergency services
    services = EmergencyService.objects.all()
    
    # Filter by category if provided
    if category:
        services = services.filter(category=category)
    
    # Calculate distances
    service_distances = []
    for service in services:
        # Skip services without coordinates
        if not service.latitude or not service.longitude:
            continue
            
        distance = calculate_distance(
            latitude, longitude,
            service.latitude, service.longitude
        )
        service_distances.append((service, distance))
    
    # Sort by distance and get nearest
    service_distances.sort(key=lambda x: x[1])
    nearest = service_distances[:count]
    
    # Format results
    result = []
    for service, distance in nearest:
        result.append({
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'address': service.address,
            'locality': service.locality,
            'distance': round(distance, 2),  # Round to 2 decimal places
            'latitude': float(service.latitude),
            'longitude': float(service.longitude)
        })
    
    return result