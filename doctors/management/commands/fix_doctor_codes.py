"""
Management command to fix duplicate doctor codes
"""

from django.core.management.base import BaseCommand
from subscription.models import Company
from subscription.db_router import set_tenant_db, clear_tenant_db
from doctors.models import Doctor
import sys


class Command(BaseCommand):
    help = 'Fix duplicate doctor codes across all tenant databases'

    def handle(self, *args, **options):
        sys.stdout.reconfigure(encoding='utf-8')
        
        companies = Company.objects.all()
        
        if not companies.exists():
            self.stdout.write(self.style.ERROR('No companies found!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {companies.count()} companies\n'))
        
        total_fixed = 0
        
        for company in companies:
            if not company.db_name:
                self.stdout.write(self.style.WARNING(f'Skipping {company.name} (no database)'))
                continue
            
            self.stdout.write(self.style.WARNING(f'\n=== Checking {company.name} ({company.db_name}) ==='))
            
            # Set tenant database context
            set_tenant_db(company.db_name)
            
            try:
                # Find doctors with duplicate or default codes
                doctors_to_fix = Doctor.objects.filter(code='000000') | Doctor.objects.filter(code='')
                
                if doctors_to_fix.exists():
                    self.stdout.write(f'  Found {doctors_to_fix.count()} doctors with duplicate/empty codes')
                    
                    for doctor in doctors_to_fix:
                        old_code = doctor.code
                        # Force regeneration by setting to empty
                        doctor.code = ''
                        doctor.save()
                        self.stdout.write(self.style.SUCCESS(
                            f'  [OK] Fixed: {doctor.ad} ({old_code} → {doctor.code})'
                        ))
                        total_fixed += 1
                else:
                    self.stdout.write('  [OK] No duplicate codes found')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
            finally:
                clear_tenant_db()
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Fixed {total_fixed} doctor codes!'))

