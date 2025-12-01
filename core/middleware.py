"""
Dual Session Middleware
Allows Django Admin and regular site to use separate session cookies
- Admin uses: admin_sessionid
- Regular site uses: sessionid
"""

import time

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.cache import patch_vary_headers
from django.utils.http import http_date


class DualSessionMiddleware(SessionMiddleware):
    """
    Custom session middleware that uses different cookies for admin and regular site.
    
    - /admin/ URLs use 'admin_sessionid' cookie
    - All other URLs use 'sessionid' cookie (default)
    
    This allows superusers to stay logged in to admin panel
    while regular users log in/out on the main site without conflicts.
    """
    
    def process_request(self, request):
        # Determine which cookie name to use based on URL path
        if request.path.startswith('/admin/'):
            # Admin panel uses separate cookie
            cookie_name = 'admin_sessionid'
        else:
            # Regular site uses default cookie
            cookie_name = settings.SESSION_COOKIE_NAME
        
        # Get the session key from the appropriate cookie
        session_key = request.COOKIES.get(cookie_name)
        
        # Set the session key on the request
        request.session = self.SessionStore(session_key)
        
        # Store the cookie name for use in process_response
        request._session_cookie_name = cookie_name
    
    def process_response(self, request, response):
        """
        Save the session and set the appropriate cookie.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response
        
        # Get the cookie name we determined in process_request
        cookie_name = getattr(request, '_session_cookie_name', settings.SESSION_COOKIE_NAME)
        
        # If the session has been modified or accessed, save it
        if accessed:
            patch_vary_headers(response, ('Cookie',))
        
        if modified or settings.SESSION_SAVE_EVERY_REQUEST:
            if request.session.get_expire_at_browser_close():
                max_age = None
                expires = None
            else:
                max_age = request.session.get_expiry_age()
                expires_time = time.time() + max_age
                expires = http_date(expires_time)
            
            # Save the session
            if empty:
                # If the session is empty, delete it
                request.session.delete()
                response.delete_cookie(
                    cookie_name,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                )
            else:
                # Save session and set cookie with the appropriate name
                request.session.save()
                response.set_cookie(
                    cookie_name,
                    request.session.session_key,
                    max_age=max_age,
                    expires=expires,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    path=settings.SESSION_COOKIE_PATH,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                )
        
        return response

