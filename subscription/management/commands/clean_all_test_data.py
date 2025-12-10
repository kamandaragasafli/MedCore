"""
Management command to clean all test data and prepare for production deployment.
This removes:
- All test companies
- All test users (except superusers)
- All subscriptions
- All tenant databases
- All user profiles
- All contract agreements
- All notifications
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from subscription.models import Company, Subscription, UserProfile, ContractAgreement, Notification
import sys


class Command(BaseCommand):
    help = 'Clean all test data and prepare for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all test data',
        )

    def handle(self, *args, **options):
        sys.stdout.reconfigure(encoding='utf-8')
        
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  WARNING: This will delete ALL test data!\n\n'
                    'This includes:\n'
                    '  - All companies\n'
                    '  - All users (except superusers)\n'
                    '  - All subscriptions\n'
                    '  - All tenant databases\n'
                    '  - All user profiles\n'
                    '  - All contract agreements\n'
                    '  - All notifications\n\n'
                    'To proceed, run: python manage.py clean_all_test_data --confirm\n'
                )
            )
            return

        with transaction.atomic():
            # Count items before deletion
            companies_count = Company.objects.count()
            users_count = User.objects.filter(is_superuser=False).count()
            subscriptions_count = Subscription.objects.count()
            profiles_count = UserProfile.objects.count()
            contracts_count = ContractAgreement.objects.count()
            notifications_count = Notification.objects.count()
            
            self.stdout.write(self.style.WARNING('\nStarting cleanup...\n'))
            
            # Delete notifications
            self.stdout.write('Deleting notifications...')
            Notification.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {notifications_count} notifications'))
            
            # Delete contract agreements
            self.stdout.write('Deleting contract agreements...')
            ContractAgreement.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {contracts_count} contract agreements'))
            
            # Delete subscriptions
            self.stdout.write('Deleting subscriptions...')
            Subscription.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {subscriptions_count} subscriptions'))
            
            # Delete user profiles
            self.stdout.write('Deleting user profiles...')
            UserProfile.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {profiles_count} user profiles'))
            
            # Delete non-superuser users
            self.stdout.write('Deleting test users...')
            deleted_users = User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {users_count} test users'))
            
            # Delete companies
            self.stdout.write('Deleting companies...')
            Company.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Deleted {companies_count} companies'))
            
            # Delete tenant database files
            self.stdout.write('\nDeleting tenant database files...')
            tenant_db_dir = os.path.join(os.getcwd(), 'tenant_databases')
            deleted_dbs = 0
            
            if os.path.exists(tenant_db_dir):
                for filename in os.listdir(tenant_db_dir):
                    if filename.startswith('tenant_') and filename.endswith('.sqlite3'):
                        filepath = os.path.join(tenant_db_dir, filename)
                        try:
                            os.remove(filepath)
                            deleted_dbs += 1
                            self.stdout.write(f'  ✓ Deleted {filename}')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'  ✗ Error deleting {filename}: {e}'))
            
            if deleted_dbs > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ Deleted {deleted_dbs} tenant database files'))
            else:
                self.stdout.write(self.style.WARNING('  No tenant database files found'))

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Successfully cleaned all test data!\n'
                'The system is now ready for production deployment.\n'
            )
        )

