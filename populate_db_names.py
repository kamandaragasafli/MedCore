"""
Populate db_name for existing companies and create their databases
Run this once: python populate_db_names.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from subscription.models import Company
from subscription.utils import generate_db_name, create_tenant_database


def populate_db_names():
    print("Populating db_name for existing companies...\n")
    
    companies = Company.objects.filter(db_name__isnull=True)
    
    if not companies.exists():
        print("No companies need db_name population.")
        return
    
    print(f"Found {companies.count()} companies without db_name\n")
    
    for company in companies:
        # Generate db_name from slug
        db_name = generate_db_name(company.slug)
        
        # Update company
        company.db_name = db_name
        company.save()
        
        print(f"Company: {company.name}")
        print(f"  Slug: {company.slug}")
        print(f"  DB Name: {db_name}")
        
        # Create database for this company
        print(f"  Creating database...")
        success = create_tenant_database(company)
        
        if success:
            print(f"  [OK] Database created successfully\n")
        else:
            print(f"  [ERROR] Failed to create database\n")
    
    print("\n[SUCCESS] All companies now have databases!")


if __name__ == '__main__':
    populate_db_names()

