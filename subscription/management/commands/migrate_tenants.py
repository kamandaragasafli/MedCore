"""
Management command to migrate all tenant databases
Usage: python manage.py migrate_tenants
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from subscription.models import Company


class Command(BaseCommand):
    help = 'Run migrations on all tenant databases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company',
            type=str,
            help='Migrate specific company by slug',
        )

    def handle(self, *args, **options):
        company_slug = options.get('company')
        
        if company_slug:
            # Migrate specific company
            try:
                company = Company.objects.get(slug=company_slug)
                self.stdout.write(f'Migrating database for: {company.name}')
                call_command('migrate', database=company.db_name)
                self.stdout.write(self.style.SUCCESS(f'[OK] Migrated {company.name}'))
            except Company.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Company not found: {company_slug}'))
        else:
            # Migrate all companies
            companies = Company.objects.all()
            
            if not companies.exists():
                self.stdout.write(self.style.WARNING('No companies found'))
                return
            
            self.stdout.write(f'Found {companies.count()} companies')
            
            for company in companies:
                self.stdout.write(f'Migrating: {company.name} ({company.db_name})')
                try:
                    call_command('migrate', database=company.db_name, verbosity=0)
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Success'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  [ERROR] Error: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS('\nAll tenant migrations complete!'))

