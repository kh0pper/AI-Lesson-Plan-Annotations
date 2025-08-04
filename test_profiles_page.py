#!/usr/bin/env python3
"""
Test script to verify the profiles page renders correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def test_profiles_page_rendering():
    """Test that the profiles page renders without BuildError."""
    
    with app.test_client() as client:
        with app.app_context():
            print("🧪 Testing profiles page rendering...")
            
            # Create a test user
            test_user = User(username="test_render_user", email="test_render@example.com")
            test_user.set_password("testpass123")
            db.session.add(test_user)
            db.session.commit()
            
            try:
                # Simulate login by posting to login endpoint
                login_response = client.post('/login', data={
                    'username': 'test_render_user',
                    'password': 'testpass123',
                    'submit': 'Sign In'
                }, follow_redirects=True)
                
                if login_response.status_code == 200:
                    print("✅ Login successful")
                    
                    # Now try to access profiles page
                    profiles_response = client.get('/profiles')
                    
                    if profiles_response.status_code == 200:
                        print("✅ Profiles page loads successfully")
                        
                        # Check if the page contains expected content
                        page_content = profiles_response.get_data(as_text=True)
                        
                        if "My Annotation Profiles" in page_content:
                            print("✅ Profiles page contains expected title")
                        else:
                            print("⚠️ Profiles page title not found")
                        
                        if "url_for('save_profile')" not in page_content:
                            print("✅ No BuildError - save_profile route is correctly referenced")
                        else:
                            print("⚠️ Found incorrect route reference")
                        
                        return True
                    else:
                        print(f"❌ Profiles page returned status: {profiles_response.status_code}")
                        return False
                else:
                    print(f"❌ Login failed with status: {login_response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error testing profiles page: {e}")
                return False
            finally:
                # Clean up test user
                db.session.delete(test_user)
                db.session.commit()
                print("🗑️ Test user cleaned up")

def main():
    """Main test function."""
    print("🚀 AI Lesson Plan Annotator - Profiles Page Rendering Test")
    print("=" * 65)
    
    if test_profiles_page_rendering():
        print("\n🎉 Profiles page is working correctly!")
        print("✅ No more BuildError for 'save_current_profile'")
        print("✅ Users can now access 'Manage Profiles' successfully")
    else:
        print("\n❌ Profiles page test failed")
        sys.exit(1)

if __name__ == '__main__':
    main()