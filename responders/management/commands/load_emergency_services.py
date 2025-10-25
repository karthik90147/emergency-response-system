from django.core.management.base import BaseCommand
from responders.models import EmergencyService

class Command(BaseCommand):
    help = 'Load emergency services data for Hyderabad'

    def handle(self, *args, **kwargs):
        # Clear existing data
        EmergencyService.objects.all().delete()
        
        # Sample coordinates for Hyderabad locations
        # These are approximate and would need to be replaced with actual coordinates
        coordinates = {
            'Afzal Gunj': (17.3616, 78.4747),
            'Musheerabad': (17.4239, 78.4958),
            'Jubilee Hills': (17.4326, 78.4071),
            'Gachibowli': (17.4401, 78.3489),
            'HITEC City': (17.4435, 78.3772),
            'Somajiguda': (17.4236, 78.4631),
            'Banjara Hills': (17.4156, 78.4347),
            'Secunderabad': (17.4399, 78.4983),
            'Nampally': (17.3939, 78.4677),
            'Old City - Gowliguda': (17.3775, 78.4866),
            'Kukatpally': (17.4849, 78.4138),
            'Kachiguda': (17.3975, 78.5069),
            'Abids': (17.3939, 78.4739),
            'Amberpet': (17.4023, 78.5214),
            'Asifnagar': (17.3616, 78.4420),
            'Bahadurpura': (17.3567, 78.4420),
            'Bowenpally': (17.4674, 78.4983),
            'Charminar': (17.3616, 78.4747),
            'Chandrayangutta': (17.3219, 78.4958),
            'Chatrinaka': (17.3567, 78.4677),
        }
        
        # Hospital data
        hospitals = [
            {
                'name': 'Osmania General Hospital',
                'address': 'Afzal Gunj, Hyderabad, Telangana',
                'locality': 'Afzal Gunj',
                'pincode': '500012',
                'source': 'https://hyderabad.telangana.gov.in/hospitals/',
            },
            {
                'name': 'Gandhi Hospital',
                'address': 'Musheerabad, Hyderabad, Telangana',
                'locality': 'Musheerabad',
                'pincode': '500020',
                'source': 'https://prognohealth.com/blog/list-of-government-hospitals-in-hyderabad/',
            },
            {
                'name': 'Apollo Hospitals, Jubilee Hills',
                'address': 'Jubilee Hills, Hyderabad, Telangana',
                'locality': 'Jubilee Hills',
                'pincode': '500033',
                'source': 'https://www.practo.com/hyderabad/hospitals',
            },
            {
                'name': 'AIG Hospitals (Asian Institute of Gastroenterology)',
                'address': 'Gachibowli Road / HITEC City area, Hyderabad',
                'locality': 'Gachibowli/HITEC City',
                'pincode': '500032',
                'source': 'https://www.practo.com/hyderabad/hospitals',
            },
            {
                'name': 'Yashoda Hospitals, Somajiguda',
                'address': 'Somajiguda, Hyderabad, Telangana',
                'locality': 'Somajiguda',
                'pincode': '500082',
                'source': 'https://en.wikipedia.org/wiki/Yashoda_Hospitals',
            },
            {
                'name': 'Care Hospitals, Banjara Hills',
                'address': 'Banjara Hills, Road No.1, Hyderabad',
                'locality': 'Banjara Hills',
                'pincode': '500034',
                'source': 'https://www.practo.com/hyderabad/hospitals',
            },
            {
                'name': 'KIMS Hospitals, Secunderabad',
                'address': 'Secunderabad, Hyderabad Metropolitan Area',
                'locality': 'Secunderabad',
                'pincode': '500025',
                'source': 'https://www.practo.com/hyderabad/hospitals',
            },
            {
                'name': 'Rainbow Children\'s Hospital',
                'address': 'Banjara Hills, Hyderabad',
                'locality': 'Banjara Hills',
                'pincode': '500034',
                'source': 'https://www.practo.com/hyderabad/hospitals',
            },
            {
                'name': 'Continental Hospitals',
                'address': 'Gachibowli, Hyderabad',
                'locality': 'Gachibowli',
                'pincode': '500032',
                'source': 'https://www.practo.com/hyderabad/hospitals',
            },
            {
                'name': 'Deccan Hospital (Government)',
                'address': 'Nampally/Osmania University area',
                'locality': 'Nampally',
                'pincode': '500001',
                'source': 'https://hyderabad.telangana.gov.in/hospitals/',
            },
        ]
        
        # Fire station data
        fire_stations = [
            {
                'name': 'Osmania Fire Station (Ghansi Bazaar)',
                'address': 'Ghansi Bazaar / Afzal Gunj area, Hyderabad',
                'locality': 'Afzal Gunj',
                'pincode': '500012',
                'source': 'https://fire.telangana.gov.in/WebSite/knowurfstn.aspx',
            },
            {
                'name': 'Gowliguda Fire Station',
                'address': 'Gowliguda, Old City, Hyderabad',
                'locality': 'Old City - Gowliguda',
                'pincode': '500012',
                'source': 'https://www.justdial.com/Hyderabad/Fire-Brigade-Services/nct-11118518',
            },
            {
                'name': 'Secunderabad Fire Station',
                'address': 'Secunderabad Cantonment area',
                'locality': 'Secunderabad',
                'pincode': '500003',
                'source': 'https://fire.telangana.gov.in/',
            },
            {
                'name': 'Kukatpally Fire Station',
                'address': 'Kukatpally, Hyderabad',
                'locality': 'Kukatpally',
                'pincode': '500072',
                'source': 'https://data.opencity.in/dataset/hyderabad-fire-stations',
            },
            {
                'name': 'Kachiguda Fire Station',
                'address': 'Kachiguda, Hyderabad',
                'locality': 'Kachiguda',
                'pincode': '500027',
                'source': 'https://fire.telangana.gov.in/',
            },
        ]
        
        # Police station data
        police_stations = [
            {
                'name': 'ABIDS Police Station',
                'address': 'Abids, Hyderabad',
                'locality': 'Abids',
                'pincode': '500001',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Afzalgunj Police Station',
                'address': 'Afzalgunj, Hyderabad',
                'locality': 'Afzal Gunj',
                'pincode': '500012',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Amberpet Police Station',
                'address': 'Amberpet, Hyderabad',
                'locality': 'Amberpet',
                'pincode': '500013',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Asifnagar Police Station',
                'address': 'Asifnagar, Hyderabad',
                'locality': 'Asifnagar',
                'pincode': '500028',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Bahadurpura Police Station',
                'address': 'Bahadurpura, Hyderabad',
                'locality': 'Bahadurpura',
                'pincode': '500064',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Banjara Hills Police Station',
                'address': 'Banjara Hills, Road No.3, Hyderabad',
                'locality': 'Banjara Hills',
                'pincode': '500034',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Bowenpally Police Station',
                'address': 'Bowenpally, near Bowenpally Police Lines',
                'locality': 'Bowenpally',
                'pincode': '500011',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Charminar Police Station',
                'address': 'Beside Charminar Monument, Old City',
                'locality': 'Charminar',
                'pincode': '500002',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Chandrayangutta Police Station',
                'address': 'Chandrayangutta, Hyderabad',
                'locality': 'Chandrayangutta',
                'pincode': '500005',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
            {
                'name': 'Chatrinaka Police Station',
                'address': 'Chatrinaka, Nagulchinta area',
                'locality': 'Chatrinaka',
                'pincode': '500053',
                'source': 'https://hyderabad.telangana.gov.in/public-utility-category/police-stations/',
            },
        ]
        
        # Create hospital records
        for hospital in hospitals:
            lat, lng = coordinates.get(hospital['locality'].split('/')[0].strip(), (None, None))
            EmergencyService.objects.create(
                name=hospital['name'],
                category='Hospital',
                address=hospital['address'],
                locality=hospital['locality'],
                pincode=hospital['pincode'],
                source=hospital['source'],
                latitude=lat,
                longitude=lng
            )
        
        # Create fire station records
        for station in fire_stations:
            lat, lng = coordinates.get(station['locality'].split('/')[0].strip(), (None, None))
            EmergencyService.objects.create(
                name=station['name'],
                category='Fire Station',
                address=station['address'],
                locality=station['locality'],
                pincode=station['pincode'],
                source=station['source'],
                latitude=lat,
                longitude=lng
            )
        
        # Create police station records
        for station in police_stations:
            lat, lng = coordinates.get(station['locality'].split('/')[0].strip(), (None, None))
            EmergencyService.objects.create(
                name=station['name'],
                category='Police Station',
                address=station['address'],
                locality=station['locality'],
                pincode=station['pincode'],
                source=station['source'],
                latitude=lat,
                longitude=lng
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(hospitals)} hospitals, {len(fire_stations)} fire stations, and {len(police_stations)} police stations'))