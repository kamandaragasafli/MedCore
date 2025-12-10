"""
Multi-Tenant Database Router
Routes database operations to company-specific databases
"""

import threading

# Thread-local storage for current tenant
_thread_locals = threading.local()


def set_tenant_db(db_name):
    """Set the database for the current request/thread"""
    setattr(_thread_locals, 'db_name', db_name)


def get_tenant_db():
    """Get the current tenant database name"""
    return getattr(_thread_locals, 'db_name', 'default')


def clear_tenant_db():
    """Clear the tenant database setting"""
    setattr(_thread_locals, 'db_name', None)


class TenantDatabaseRouter:
    """
    Routes database operations to company-specific databases.
    
    - subscription app models go to 'default' (master database)
    - All other models go to tenant-specific database
    """
    
    # Apps that should always use the master database
    MASTER_APPS = ['subscription', 'auth', 'contenttypes', 'sessions', 'admin', 'master_admin']
    
    def db_for_read(self, model, **hints):
        """Route read operations"""
        # Master database apps
        if model._meta.app_label in self.MASTER_APPS:
            return 'default'
        
        # Get tenant database
        tenant_db = get_tenant_db()
        return tenant_db if tenant_db else 'default'
    
    def db_for_write(self, model, **hints):
        """Route write operations"""
        # Master database apps
        if model._meta.app_label in self.MASTER_APPS:
            return 'default'
        
        # Get tenant database
        tenant_db = get_tenant_db()
        return tenant_db if tenant_db else 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations only between objects in the same database
        """
        db1 = obj1._state.db
        db2 = obj2._state.db
        
        # Allow if both are in master database
        if db1 == 'default' and db2 == 'default':
            return True
        
        # Allow if both are in the same tenant database
        if db1 == db2:
            return True
        
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Control which apps can be migrated to which databases
        """
        # Master apps only migrate to default database
        if app_label in self.MASTER_APPS:
            return db == 'default'
        
        # Tenant apps can migrate to any database except default
        if db == 'default':
            return False
        
        return True

