"""
Management command to list all tenant databases
Usage: python manage.py list_tenants
"""

from django.core.management.base import BaseCommand
from subscription.models import Company
from pathlib import Path


class Command(BaseCommand):
    help = 'List all tenant databases'

    def handle(self, *args, **options):
        companies = Company.objects.all()
        
        if not companies.exists():
            self.stdout.write(self.style.WARNING('No companies found'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\nFound {companies.count()} companies:\n'))
        
        for idx, company in enumerate(companies, 1):
            self.stdout.write(f'{idx}. {company.name}')
            self.stdout.write(f'   Slug: {company.slug}')
            self.stdout.write(f'   DB Name: {company.db_name}')
            self.stdout.write(f'   Email: {company.email}')
            self.stdout.write(f'   Status: {"Active" if company.is_active else "Inactive"}')
            self.stdout.write(f'   Users: {company.users_count}')
            
            subscription = company.active_subscription
            if subscription:
                self.stdout.write(f'   Subscription: {subscription.plan.name} ({subscription.status})')
                self.stdout.write(f'   Days remaining: {subscription.days_remaining}')
            else:
                self.stdout.write(f'   Subscription: None')
            
            self.stdout.write('')

