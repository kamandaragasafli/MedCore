from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from .models import UserProfile, Company, ContractAgreement
from .db_router import set_tenant_db, clear_tenant_db


class TenantMiddleware(MiddlewareMixin):
    """
    Multi-Tenant Middleware
    - Sets the current company context for authenticated users
    - Routes database queries to company-specific database
    - Handles superusers accessing dashboard
    """
    
    def process_request(self, request):
        # Skip ONLY for master-admin URLs
        if request.path.startswith('/master-admin/'):
            clear_tenant_db()
            return None
        
        if request.user.is_authenticated:
            # Check if superuser is impersonating a company
            if request.user.is_superuser and request.session.get('impersonating_company_id'):
                try:
                    impersonated_company = Company.objects.get(id=request.session['impersonating_company_id'])
                    request.company = impersonated_company
                    request.user_profile = None
                    request.user_role = 'master_admin'
                    
                    # Set the tenant database for impersonated company
                    if impersonated_company.db_name:
                        set_tenant_db(impersonated_company.db_name)
                    else:
                        clear_tenant_db()
                    
                    return None
                except Company.DoesNotExist:
                    # Invalid company ID, clear impersonation
                    request.session.pop('impersonating_company_id', None)
                    request.session.pop('impersonating_company_name', None)
                    request.session.pop('master_admin_mode', None)
            
            try:
                # Get user profile with company
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                company = profile.company
                request.company = company
                request.user_profile = profile
                request.user_role = profile.role
                
                # Get unread notification count for template context
                # This will be handled by context processor
                
                # Check contract agreement (skip for contract and subscription pages)
                if (not request.path.startswith('/subscription/contract') and 
                    not request.path.startswith('/subscription/plans') and
                    not request.path.startswith('/subscription/register') and
                    not request.path.startswith('/admin/') and
                    not request.path.startswith('/master-admin/')):
                    try:
                        contract = ContractAgreement.objects.get(
                            company=profile.company, 
                            user=request.user
                        )
                        request.contract_agreed = contract.agreed
                    except ContractAgreement.DoesNotExist:
                        request.contract_agreed = False
                else:
                    request.contract_agreed = True  # Skip check for these pages
                
                # Set the tenant database for this request
                if profile.company and profile.company.db_name:
                    set_tenant_db(profile.company.db_name)
                else:
                    clear_tenant_db()
                    
            except UserProfile.DoesNotExist:
                # For superusers, try to get first company as fallback
                if request.user.is_superuser or request.user.is_staff:
                    first_company = Company.objects.first()
                    if first_company:
                        request.company = first_company
                        request.user_profile = None
                        request.user_role = 'admin'
                        if first_company.db_name:
                            set_tenant_db(first_company.db_name)
                    else:
                        request.company = None
                        request.user_profile = None
                        request.user_role = None
                        clear_tenant_db()
                else:
                    request.company = None
                    request.user_profile = None
                    request.user_role = None
                    clear_tenant_db()
        else:
            request.company = None
            request.user_profile = None
            request.user_role = None
            clear_tenant_db()
        
        return None
    
    def process_response(self, request, response):
        """Clear tenant database after request completes"""
        clear_tenant_db()
        return response
    
    def process_exception(self, request, exception):
        """Clear tenant database on exception"""
        clear_tenant_db()
        return None

