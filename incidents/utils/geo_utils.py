from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

class GeoLocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="emergency_response_system")
    
    def reverse_geocode(self, latitude, longitude):
        """
        Convert coordinates to address
        """
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
            if location:
                return location.address
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding error: {e}")
            return None
    
    def geocode_address(self, address):
        """
        Convert address to coordinates
        """
        try:
            location = self.geolocator.geocode(address, timeout=10)
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address
                }
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding error: {e}")
            return None
