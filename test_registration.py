#!/usr/bin/env python3
"""
Test script to verify user registration is working properly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def test_registration():
    """Test user registration functionality."""
    with app.app_context():
        print("🧪 Testing user registration system...")
        
        # Check if database is accessible
        try:
            user_count = User.query.count()
            print(f"✅ Database connection: {user_count} users currently registered")
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        
        # Test user creation
        test_username = "testuser_automated"
        test_email = "test_automated@example.com"
        
        # Check if test user already exists
        existing_user = User.query.filter_by(username=test_username).first()
        if existing_user:
            print(f"🗑️ Removing existing test user: {test_username}")
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create new test user
        try:
            test_user = User(username=test_username, email=test_email)
            test_user.set_password("testpassword123")
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"✅ User created successfully: {test_username}")
            
            # Verify user was saved
            saved_user = User.query.filter_by(username=test_username).first()
            if saved_user:
                print(f"✅ User retrieved from database: {saved_user.username}")
                print(f"   Email: {saved_user.email}")
                print(f"   Created: {saved_user.created_at}")
                print(f"   Premium status: {saved_user.is_premium()}")
                print(f"   Profile limit: {saved_user.get_profile_limit()}")
                print(f"   Hourly limit: {saved_user.get_hourly_usage_limit()}")
                
                # Test password verification
                if saved_user.check_password("testpassword123"):
                    print("✅ Password verification works")
                else:
                    print("❌ Password verification failed")
                    return False
                
                # Clean up test user
                db.session.delete(saved_user)
                db.session.commit()
                print("🗑️ Test user cleaned up")
                
                return True
            else:
                print("❌ User not found after creation")
                return False
                
        except Exception as e:
            print(f"❌ User creation failed: {e}")
            return False

def main():
    """Main test function."""
    print("🚀 AI Lesson Plan Annotator - Registration Test")
    print("=" * 50)
    
    if test_registration():
        print("\n🎉 Registration system is working perfectly!")
        print("\n✅ You can now register new users at: http://localhost:5000/register")
    else:
        print("\n❌ Registration test failed")
        sys.exit(1)

if __name__ == '__main__':
    main()