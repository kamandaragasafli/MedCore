"""
Management command to populate initial regions data for ALL tenant databases
"""

from django.core.management.base import BaseCommand
from subscription.models import Company
from subscription.db_router import set_tenant_db, clear_tenant_db
from regions.models import Region, City, Clinic, Specialization


class Command(BaseCommand):
    help = 'Populate initial regions data for all tenant databases'

    def handle(self, *args, **options):
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
        
        companies = Company.objects.all()
        
        if not companies.exists():
            self.stdout.write(self.style.ERROR('No companies found!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {companies.count()} companies\n'))
        
        for company in companies:
            if not company.db_name:
                self.stdout.write(self.style.WARNING(f'Skipping {company.name} (no database)'))
                continue
            
            self.stdout.write(self.style.WARNING(f'\n=== Populating {company.name} ({company.db_name}) ==='))
            
            # Set tenant database context
            set_tenant_db(company.db_name)
            
            try:
                self.populate_data()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            finally:
                clear_tenant_db()
        
        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] All tenants populated!'))
    
    def populate_data(self):
        # Create Regions
        regions_data = [
            {'name': 'Bakı', 'code': 'BAK'},
            {'name': 'Gəncə', 'code': 'GAN'},
            {'name': 'Sumqayıt', 'code': 'SMQ'},
            {'name': 'Mingəçevir', 'code': 'MIN'},
            {'name': 'Abşeron', 'code': 'ABS'},
        ]
        
        regions = {}
        for data in regions_data:
            region, created = Region.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            regions[data['code']] = region
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Created region: {region.name}'))
        
        # Create Cities
        cities_data = [
            {'name': 'Bakı', 'region': 'BAK'},
            {'name': 'Sumqayıt', 'region': 'SMQ'},
            {'name': 'Gəncə', 'region': 'GAN'},
        ]
        
        cities = {}
        for data in cities_data:
            city, created = City.objects.get_or_create(
                name=data['name'],
                region=regions[data['region']],
            )
            cities[data['name']] = city
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Created city: {city.name}'))
        
        # Create Clinics
        clinics_data = [
            {
                'name': 'Bakı Mərkəzi Klinika',
                'region': 'BAK',
                'city': 'Bakı',
                'address': 'Nəsimi rayonu, 28 May küç. 15',
                'phone': '+994 12 555 0000',
                'type': 'clinic'
            },
            {
                'name': 'Respublika Xəstəxanası',
                'region': 'BAK',
                'city': 'Bakı',
                'address': 'Yasamal rayonu, Ə. Rəcəbli küç. 32',
                'phone': '+994 12 555 1111',
                'type': 'hospital'
            },
            {
                'name': 'Təbabət Mərkəzi №3',
                'region': 'BAK',
                'city': 'Bakı',
                'address': 'Nərimanov rayonu, S. Vəzirov küç. 10',
                'phone': '+994 12 555 2222',
                'type': 'medical_center'
            },
            {
                'name': 'Sumqayıt Şəhər Poliklinikası',
                'region': 'SMQ',
                'city': 'Sumqayıt',
                'address': 'Sumqayıt şəhəri, 17-ci mikrorayon',
                'phone': '+994 18 555 3333',
                'type': 'polyclinic'
            },
            {
                'name': 'Gəncə Mərkəzi Xəstəxana',
                'region': 'GAN',
                'city': 'Gəncə',
                'address': 'Gəncə şəhəri, Nizami küç. 25',
                'phone': '+994 22 555 4444',
                'type': 'hospital'
            },
            {
                'name': 'Gəncə Diaqnostika Mərkəzi',
                'region': 'GAN',
                'city': 'Gəncə',
                'address': 'Gəncə şəhəri, Heydər Əliyev prospekti 45',
                'phone': '+994 22 555 5555',
                'type': 'medical_center'
            },
            {
                'name': 'Abşeron Rayon Klinikası',
                'region': 'ABS',
                'city': 'Bakı',
                'address': 'Abşeron rayonu, Xırdalan şəhəri',
                'phone': '+994 12 555 6666',
                'type': 'clinic'
            },
        ]
        
        for data in clinics_data:
            clinic, created = Clinic.objects.get_or_create(
                name=data['name'],
                defaults={
                    'region': regions[data['region']],
                    'city': cities[data['city']],
                    'address': data['address'],
                    'phone': data['phone'],
                    'type': data['type'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Created clinic: {clinic.name}'))
        
        # Create Specializations
        specializations_data = [
            'Terapevt',
            'Kardioloq',
            'Nevroloq',
            'Pediatr',
            'Cərrah',
            'Ortoped',
            'Dermatoloq',
            'Endokrinoloq',
            'Uşaq həkimi',
            'Ginekoloq',
        ]
        
        for name in specializations_data:
            spec, created = Specialization.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Created specialization: {spec.name}'))
        
        self.stdout.write(f'  Summary: {Region.objects.count()} regions, {City.objects.count()} cities, {Clinic.objects.count()} clinics, {Specialization.objects.count()} specializations')

