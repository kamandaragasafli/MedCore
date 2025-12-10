"""
Management command to create a database for a specific tenant
Usage: python manage.py create_tenant_db <company_slug>
"""

from django.core.management.base import BaseCommand, CommandError
from subscription.models import Company
from subscription.utils import create_tenant_database


class Command(BaseCommand):
    help = 'Create database for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument(
            'company_slug',
            type=str,
            help='Company slug to create database for',
        )

    def handle(self, *args, **options):
        company_slug = options['company_slug']
        
        try:
            company = Company.objects.get(slug=company_slug)
        except Company.DoesNotExist:
            raise CommandError(f'Company not found: {company_slug}')
        
        self.stdout.write(f'Creating database for: {company.name}')
        
        success = create_tenant_database(company)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'[OK] Database created successfully'))
            self.stdout.write(f'Database name: {company.db_name}')
        else:
            self.stdout.write(self.style.ERROR(f'[ERROR] Failed to create database'))

