from django.core.management.base import BaseCommand
from responders.models import Responder
import random

class Command(BaseCommand):
    help = 'Simulate responder location updates'

    def handle(self, *args, **options):
        responders = Responder.objects.filter(is_active=True)
        
        # Bengaluru coordinates range
        base_lat = 12.9716
        base_lon = 77.5946
        
        for responder in responders:
            # Simulate location within 10km radius
            lat_offset = random.uniform(-0.1, 0.1)
            lon_offset = random.uniform(-0.1, 0.1)
            
            responder.current_latitude = base_lat + lat_offset
            responder.current_longitude = base_lon + lon_offset
            responder.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated location for {responder.name}')
            )
        
        self.stdout.write(self.style.SUCCESS('All responder locations updated!'))
