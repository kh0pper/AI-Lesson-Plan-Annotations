#!/usr/bin/env python3
"""
Script to manually update user subscription status to premium.
Use this if Stripe webhooks aren't working or you need to fix subscription status.
"""

from app import app
from models import db, User

def update_user_subscription(username_or_email, status='active'):
    """Update a user's subscription status."""
    
    with app.app_context():
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user:
            print(f"❌ User not found: {username_or_email}")
            return False
        
        print(f"📝 Found user: {user.username} ({user.email})")
        print(f"   Current status: {user.subscription_status}")
        
        # Update subscription status
        user.subscription_status = status
        db.session.commit()
        
        print(f"✅ Updated subscription status to: {status}")
        print(f"   Profile limit: {user.get_profile_limit()}")
        print(f"   Is premium: {user.is_premium()}")
        
        return True

def list_all_users():
    """List all users and their subscription status."""
    
    with app.app_context():
        users = User.query.all()
        
        print("👥 All users:")
        print("-" * 50)
        
        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Status: {user.subscription_status}")
            print(f"Premium: {user.is_premium()}")
            print(f"Profile limit: {user.get_profile_limit()}")
            print(f"Profiles: {len(user.annotation_profiles)}")
            print("-" * 30)

if __name__ == '__main__':
    print("🎓 AI Lesson Plan Annotator - Subscription Updater")
    print("=" * 50)
    
    # List current users
    list_all_users()
    
    # Get user input
    user_input = input("\nEnter username or email to upgrade to premium (or 'skip' to exit): ").strip()
    
    if user_input.lower() != 'skip' and user_input:
        if update_user_subscription(user_input, 'active'):
            print("\n🎉 User successfully upgraded to premium!")
            print("They can now:")
            print("- Save up to 10 custom profiles")
            print("- Run unlimited annotations")
        else:
            print("\n❌ Failed to update user subscription")
    else:
        print("👋 No changes made")