from django.apps import AppConfig


class SubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription'
    verbose_name = 'Subscription Management'
    
    def ready(self):
        """Load all tenant databases when Django starts"""
        # Only run once during startup
        import sys
        if 'runserver' in sys.argv or 'migrate' not in sys.argv:
            try:
                from .utils import load_tenant_databases
                load_tenant_databases()
            except Exception as e:
                # Silently fail during initial setup
                pass

