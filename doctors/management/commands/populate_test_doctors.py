"""
Management command to populate test doctors for all tenant databases
Generates 40 doctors per company with realistic test data
"""

from django.core.management.base import BaseCommand
from subscription.models import Company
from subscription.db_router import set_tenant_db, clear_tenant_db
from doctors.models import Doctor
from regions.models import Region, City, Clinic, Specialization
import random
import sys
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate 40 test doctors for each company'

    def handle(self, *args, **options):
        sys.stdout.reconfigure(encoding='utf-8')
        
        companies = Company.objects.all()
        
        if not companies.exists():
            self.stdout.write(self.style.ERROR('No companies found!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {companies.count()} companies\n'))
        
        # Azerbaijani names for realistic test data
        first_names_male = [
            'Əli', 'Vəli', 'Məmməd', 'Rəşid', 'Elxan', 'Tural', 'Kamran', 
            'Nicat', 'Orxan', 'Zaur', 'Fərid', 'Rəhim', 'Sənan', 'İlqar',
            'Cavid', 'Anar', 'Elvin', 'Ramil', 'Fuad', 'Murad'
        ]
        
        first_names_female = [
            'Aysel', 'Günel', 'Səbinə', 'Leyla', 'Aynur', 'Nigar', 'Sevinc',
            'Könül', 'Nərgiz', 'Şəbnəm', 'Mələk', 'Gültəkin', 'Fidan', 
            'Əsmər', 'Mehriban', 'Sevda', 'Lalə', 'Ülkər', 'Əzizə', 'Şahnaz'
        ]
        
        last_names = [
            'Məmmədov', 'Əliyev', 'Həsənov', 'Hüseynov', 'İsmayılov',
            'Quliyev', 'Nəbiyev', 'Əhmədov', 'Abbasov', 'Qasımov',
            'Rəhimov', 'Əzizov', 'Babayev', 'Səfərov', 'Əsgərov',
            'Cəfərov', 'Mustafayev', 'Vəliyev', 'Kazımov', 'Novruzov',
            'Hacıyev', 'Məcidov', 'Rüstəmov', 'Şahbazov', 'Əkbərov'
        ]
        
        total_created = 0
        
        for company in companies:
            if not company.db_name:
                self.stdout.write(self.style.WARNING(f'Skipping {company.name} (no database)'))
                continue
            
            self.stdout.write(self.style.WARNING(f'\n=== Populating {company.name} ({company.db_name}) ==='))
            
            # Set tenant database context
            set_tenant_db(company.db_name)
            
            try:
                # Get available data from tenant database
                regions = list(Region.objects.all())
                cities = list(City.objects.all())
                clinics = list(Clinic.objects.all())
                specializations = list(Specialization.objects.all())
                
                if not all([regions, cities, clinics, specializations]):
                    self.stdout.write(self.style.WARNING(
                        '  [WARN] Missing regions/cities/clinics/specializations. Run populate_all_tenants_regions first.'
                    ))
                    continue
                
                # Create 40 test doctors
                doctors_created = 0
                for i in range(40):
                    # Random gender
                    gender = random.choice(['male', 'female'])
                    
                    # Random name based on gender
                    if gender == 'male':
                        first_name = random.choice(first_names_male)
                    else:
                        first_name = random.choice(first_names_female)
                    
                    last_name = random.choice(last_names)
                    full_name = f"{last_name} {first_name}"
                    
                    # Random location
                    region = random.choice(regions) if regions else None
                    
                    # Get cities for this region
                    region_cities = [c for c in cities if c.region == region] if region and cities else []
                    city = random.choice(region_cities) if region_cities else None
                    
                    # Get clinics for this region
                    region_clinics = [cl for cl in clinics if cl.region == region] if region and clinics else []
                    clinic = random.choice(region_clinics) if region_clinics else None
                    
                    # Random professional data
                    specialization = random.choice(specializations) if specializations else None
                    category = random.choice(['A', 'B', 'C'])
                    degree = random.choice(['VIP', 'I', 'II', 'III'])
                    
                    # Random phone number
                    phone = f"+994 {random.choice([50, 51, 55, 70, 77])} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
                    
                    # Random email (optional)
                    email = None
                    if random.random() > 0.3:  # 70% have email
                        email_prefix = first_name.lower().replace('ə', 'e').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ğ', 'g').replace('ş', 's').replace('ç', 'c')
                        email = f"{email_prefix}.{last_name.lower()[:5]}@example.com"
                    
                    # Random financial data
                    evvelki_borc = Decimal(random.randint(-500000, 500000) / 100)  # -5000 to 5000
                    hesablanmish_miqdar = Decimal(random.randint(0, 1000000) / 100)  # 0 to 10000
                    silinen_miqdar = Decimal(random.randint(0, 500000) / 100)  # 0 to 5000
                    
                    # Random registration date (last 2 years)
                    from django.utils import timezone
                    from datetime import timedelta
                    days_ago = random.randint(0, 730)
                    datasiya = timezone.now().date() - timedelta(days=days_ago)
                    
                    # Create doctor
                    doctor = Doctor.objects.create(
                        ad=full_name,
                        telefon=phone,
                        email=email,
                        gender=gender,
                        region=region,
                        city=city,
                        clinic=clinic,
                        ixtisas=specialization,
                        category=category,
                        degree=degree,
                        evvelki_borc=evvelki_borc,
                        hesablanmish_miqdar=hesablanmish_miqdar,
                        silinen_miqdar=silinen_miqdar,
                        datasiya=datasiya,
                        is_active=random.choice([True, True, True, False])  # 75% active
                    )
                    
                    doctors_created += 1
                    if doctors_created % 10 == 0:
                        self.stdout.write(f'  [+] Created {doctors_created} doctors...')
                
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created {doctors_created} test doctors'))
                total_created += doctors_created
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
                import traceback
                traceback.print_exc()
            finally:
                clear_tenant_db()
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Created {total_created} test doctors across all companies!'))

