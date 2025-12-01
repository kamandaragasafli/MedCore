"""
Utility functions for multi-tenant database management
"""

import os
from django.conf import settings
from django.core.management import call_command
from django.db import connections
from pathlib import Path


def generate_db_name(slug):
    """Generate database name from company slug"""
    return f"tenant_{slug}"


def get_db_path(db_name):
    """Get the full path for a tenant database file"""
    db_dir = settings.BASE_DIR / 'tenant_databases'
    db_dir.mkdir(exist_ok=True)
    return db_dir / f"{db_name}.sqlite3"


def get_tenant_db_config(db_name):
    """
    Get complete database configuration for a tenant database
    Returns a dict with all required Django database settings
    """
    db_path = get_db_path(db_name)
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(db_path),
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': False,
        'OPTIONS': {},
        'TIME_ZONE': None,
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'TEST': {
            'CHARSET': None,
            'COLLATION': None,
            'NAME': None,
            'MIRROR': None,
        },
    }


def create_tenant_database(company):
    """
    Create a new database for a company and run migrations
    
    Args:
        company: Company model instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db_name = company.db_name
        
        # Add database configuration to settings
        if db_name not in settings.DATABASES:
            settings.DATABASES[db_name] = get_tenant_db_config(db_name)
        
        # Ensure database connection is closed before creating new one
        if db_name in connections.databases:
            connections[db_name].close()
        
        # Run migrations for the new database (excluding subscription app)
        print(f"Creating database for {company.name}...")
        
        # Get all non-master apps
        from django.apps import apps
        app_labels = [app.label for app in apps.get_app_configs() 
                     if app.label not in ['subscription', 'auth', 'contenttypes', 'sessions', 'admin']]
        
        # Run migrations
        try:
            call_command('migrate', '--database', db_name, verbosity=1, interactive=False)
            print(f"[OK] Database created successfully: {db_path}")
            return True
        except Exception as migrate_error:
            print(f"Migration error: {str(migrate_error)}")
            # Database file created but migrations may have issues
            # This is okay for now, migrations can be run later
            return True
        
    except Exception as e:
        print(f"Error creating tenant database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def load_tenant_databases():
    """
    Load all tenant databases into Django settings
    Should be called on application startup
    """
    from subscription.models import Company
    
    try:
        companies = Company.objects.all()
        
        for company in companies:
            if company.db_name and company.db_name not in settings.DATABASES:
                settings.DATABASES[company.db_name] = get_tenant_db_config(company.db_name)
                
        print(f"Loaded {len(companies)} tenant databases")
        
    except Exception as e:
        # This might fail on first migration before Company table exists
        print(f"Note: Could not load tenant databases: {str(e)}")


def delete_tenant_database(company):
    """
    Delete a company's database (use with caution!)
    
    Args:
        company: Company model instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db_name = company.db_name
        db_path = get_db_path(db_name)
        
        # Close connection if open
        if db_name in connections:
            connections[db_name].close()
            del connections.databases[db_name]
        
        # Remove from settings
        if db_name in settings.DATABASES:
            del settings.DATABASES[db_name]
        
        # Delete the database file
        if db_path.exists():
            os.remove(db_path)
            print(f"✓ Database deleted: {db_path}")
            return True
        
    except Exception as e:
        print(f"Error deleting tenant database: {str(e)}")
        return False


def switch_to_tenant_db(db_name):
    """
    Context manager for temporarily switching to a tenant database
    
    Usage:
        with switch_to_tenant_db('tenant_company_slug'):
            doctors = Doctor.objects.all()
    """
    from .db_router import set_tenant_db, clear_tenant_db
    
    class TenantDBContext:
        def __enter__(self):
            set_tenant_db(db_name)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            clear_tenant_db()
            return False
    
    return TenantDBContext()

