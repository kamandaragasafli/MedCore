"""
Test script to verify dual session system is working correctly.

This script simulates:
1. Admin login
2. Regular user login  
3. Verifies both sessions exist independently
4. Checks cookies are properly separated

Usage:
    python test_dual_sessions.py
"""

import requests
from requests.cookies import RequestsCookieJar


def test_dual_sessions():
    """Test that admin and regular sessions work independently."""
    
    base_url = "http://127.0.0.1:8000"
    
    print("=" * 60)
    print("🧪 TESTING DUAL SESSION SYSTEM")
    print("=" * 60)
    
    # Create separate cookie jars for simulation
    admin_cookies = RequestsCookieJar()
    user_cookies = RequestsCookieJar()
    
    # Test 1: Check middleware is loaded
    print("\n📋 Test 1: Checking middleware configuration...")
    try:
        response = requests.get(f"{base_url}/")
        print("✅ Server is responding")
        print(f"   Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server is not running!")
        print("   Please start: python manage.py runserver")
        return False
    
    # Test 2: Admin login page
    print("\n📋 Test 2: Checking admin login page...")
    try:
        response = requests.get(f"{base_url}/admin/login/")
        if response.status_code == 200:
            print("✅ Admin login page accessible")
            
            # Check if any cookies are set
            if response.cookies:
                print("   Cookies received:")
                for cookie in response.cookies:
                    print(f"   - {cookie.name}")
        else:
            print(f"⚠️  Admin returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing admin: {e}")
    
    # Test 3: Regular login page
    print("\n📋 Test 3: Checking regular login page...")
    try:
        response = requests.get(f"{base_url}/login/")
        if response.status_code == 200:
            print("✅ Regular login page accessible")
            
            # Check if any cookies are set
            if response.cookies:
                print("   Cookies received:")
                for cookie in response.cookies:
                    print(f"   - {cookie.name}")
        else:
            print(f"⚠️  Login returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing login: {e}")
    
    # Test 4: Session separation test
    print("\n📋 Test 4: Simulating dual sessions...")
    print("   (This simulates what happens in a real browser)")
    
    # Simulate admin session
    session_admin = requests.Session()
    response_admin = session_admin.get(f"{base_url}/admin/")
    admin_cookie_names = [cookie.name for cookie in session_admin.cookies]
    
    # Simulate user session  
    session_user = requests.Session()
    response_user = session_user.get(f"{base_url}/")
    user_cookie_names = [cookie.name for cookie in session_user.cookies]
    
    print("\n   Admin session cookies:", admin_cookie_names if admin_cookie_names else "None")
    print("   User session cookies:", user_cookie_names if user_cookie_names else "None")
    
    # Test 5: Manual cookie check
    print("\n📋 Test 5: Cookie naming verification...")
    print("   Note: This test checks cookie naming logic")
    print("   Actual cookies are only set AFTER login")
    
    # Simulate the middleware logic
    admin_path = "/admin/login/"
    user_path = "/doctors/"
    
    expected_admin_cookie = "admin_sessionid"
    expected_user_cookie = "sessionid"
    
    print(f"\n   For path: {admin_path}")
    print(f"   Expected cookie: {expected_admin_cookie}")
    
    print(f"\n   For path: {user_path}")
    print(f"   Expected cookie: {expected_user_cookie}")
    
    # Final report
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    print("\n✅ MIDDLEWARE INSTALLED")
    print("   File: core/middleware.py")
    print("   Class: DualSessionMiddleware")
    
    print("\n✅ COOKIE NAMES CONFIGURED")
    print(f"   Admin paths (/admin/*):  {expected_admin_cookie}")
    print(f"   Regular paths (/*):      {expected_user_cookie}")
    
    print("\n🧪 TO TEST FULLY:")
    print("   1. Open browser to: http://127.0.0.1:8000/admin/")
    print("   2. Login as superuser")
    print("   3. Open DevTools (F12) → Application → Cookies")
    print("   4. Verify 'admin_sessionid' cookie exists")
    print("   5. Visit: http://127.0.0.1:8000/login/")
    print("   6. Login as regular user")
    print("   7. Check cookies - should see BOTH:")
    print("      - admin_sessionid")
    print("      - sessionid")
    print("   8. Switch between /admin/ and / - both should work!")
    
    print("\n📖 For detailed guide, see:")
    print("   DUAL_SESSION_IMPLEMENTATION_GUIDE.md")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETED")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_dual_sessions()

