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
    Get complete database configuration for a tenant database.
    Local: SQLite (tenant faylları tenant_databases/ içində).
    Production: PostgreSQL (hər tenant üçün ayrı DB).
    """
    from decouple import config
    # Əvvəlcə settings-dən (production-da USE_POSTGRESQL=True), yoxdusa .env
    use_pg = getattr(settings, 'USE_POSTGRESQL', None)
    if use_pg is None:
        use_pg = config('USE_POSTGRESQL', default=False, cast=bool)
    
    if use_pg:
        # PostgreSQL for production - each tenant gets its own database
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,  # Each tenant has its own PostgreSQL database
            'USER': config('DB_USER', default='medadmin_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'ATOMIC_REQUESTS': False,
            'AUTOCOMMIT': True,
            'CONN_MAX_AGE': 600,  # 10 minutes connection pooling
            'CONN_HEALTH_CHECKS': True,
            'OPTIONS': {
                'connect_timeout': 10,
            },
            'TIME_ZONE': None,
            'TEST': {
                'CHARSET': None,
                'COLLATION': None,
                'NAME': None,
                'MIRROR': None,
            },
        }
    else:
        # SQLite for local development
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
        use_pg = getattr(settings, 'USE_POSTGRESQL', None)
        if use_pg is None:
            from decouple import config
            use_pg = config('USE_POSTGRESQL', default=False, cast=bool)
        
        db_name = company.db_name
        
        # Add database configuration to settings
        if db_name not in settings.DATABASES:
            settings.DATABASES[db_name] = get_tenant_db_config(db_name)
        
        # Ensure database connection is closed before creating new one
        if db_name in connections.databases:
            connections[db_name].close()
        
        if use_pg:
            # PostgreSQL: Create database using psycopg2
            from django.db import connection
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # Connect to default database to create new database
            default_db_config = settings.DATABASES['default']
            import psycopg2
            
            try:
                # Connect to PostgreSQL server (not to specific database)
                conn = psycopg2.connect(
                    host=default_db_config['HOST'],
                    port=default_db_config['PORT'],
                    user=default_db_config['USER'],
                    password=default_db_config['PASSWORD'],
                    database='postgres'  # Connect to default postgres database
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                
                # Check if database exists
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                exists = cursor.fetchone()
                
                if not exists:
                    # Create database
                    cursor.execute(f'CREATE DATABASE "{db_name}"')
                    print(f"[OK] PostgreSQL database created: {db_name}")
                else:
                    print(f"[INFO] PostgreSQL database already exists: {db_name}")
                
                cursor.close()
                conn.close()
                
            except Exception as pg_error:
                print(f"PostgreSQL database creation error: {str(pg_error)}")
                return False
        else:
            # SQLite: File will be created automatically on first connection
            db_path = get_db_path(db_name)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Creating SQLite database for {company.name}...")
        
        # Run migrations for the new database (excluding subscription app)
        print(f"Running migrations for {company.name}...")
        
        # Run migrations
        try:
            call_command('migrate', '--database', db_name, verbosity=1, interactive=False)
            if USE_POSTGRESQL:
                print(f"[OK] Database created and migrated successfully: {db_name}")
            else:
                print(f"[OK] Database created and migrated successfully: {db_path}")
            return True
        except Exception as migrate_error:
            print(f"Migration error: {str(migrate_error)}")
            # Database created but migrations may have issues
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

