#!/usr/bin/env python3
"""
Script to grant alpha/premium access to users without requiring Stripe subscription.
Perfect for alpha testers, beta users, or promotional access.
"""

from app import app
from models import db, User
from datetime import datetime, timedelta

def grant_alpha_access(email_or_username, duration_days=365, access_type='alpha'):
    """
    Grant alpha/premium access to a user by email or username.
    
    Args:
        email_or_username: User's email or username
        duration_days: How many days of access (default: 365 = 1 year)
        access_type: 'alpha', 'beta', 'premium', or 'lifetime'
    """
    
    with app.app_context():
        # Find user by email or username
        user = User.query.filter(
            (User.email == email_or_username) | 
            (User.username == email_or_username)
        ).first()
        
        if not user:
            print(f"❌ User not found: {email_or_username}")
            return False
        
        print(f"📧 Found user: {user.username} ({user.email})")
        print(f"📊 Current status: {user.subscription_status}")
        print(f"💎 Currently premium: {user.is_premium()}")
        
        # Set subscription details
        user.subscription_status = 'active'
        user.subscription_start = datetime.utcnow()
        
        if duration_days > 0:
            user.subscription_end = datetime.utcnow() + timedelta(days=duration_days)
        else:
            user.subscription_end = None  # Lifetime access
        
        user.last_payment = datetime.utcnow()
        
        # Add a note in subscription_id to track this is alpha access
        user.subscription_id = f"{access_type}_access_{datetime.now().strftime('%Y%m%d')}"
        
        db.session.commit()
        
        print(f"✅ SUCCESS! Granted {access_type} access to {user.username}")
        print(f"📅 Access expires: {user.subscription_end.strftime('%Y-%m-%d') if user.subscription_end else 'Never (lifetime)'}")
        print(f"🎯 Profile limit: {user.get_profile_limit()}")
        print(f"⚡ Rate limit: {'Unlimited' if user.is_premium() else '5/hour'}")
        
        return True

def list_alpha_users():
    """List all users with alpha/beta access."""
    
    with app.app_context():
        # Find users with alpha/beta access
        alpha_users = User.query.filter(
            User.subscription_id.like('%alpha_access%') |
            User.subscription_id.like('%beta_access%') |
            (User.subscription_status == 'active')
        ).all()
        
        print("🧪 Alpha/Premium Users:")
        print("=" * 60)
        
        for user in alpha_users:
            access_type = "Unknown"
            if user.subscription_id:
                if 'alpha_access' in user.subscription_id:
                    access_type = "Alpha Tester"
                elif 'beta_access' in user.subscription_id:
                    access_type = "Beta Tester"
                elif user.subscription_id.startswith('sub_'):
                    access_type = "Paid Subscriber"
                else:
                    access_type = "Premium Access"
            
            expires = user.subscription_end.strftime('%Y-%m-%d') if user.subscription_end else 'Lifetime'
            
            print(f"👤 {user.username} ({user.email})")
            print(f"   Type: {access_type}")
            print(f"   Status: {user.subscription_status}")
            print(f"   Expires: {expires}")
            print(f"   Profiles: {len(user.annotation_profiles)}/{user.get_profile_limit()}")
            print("-" * 40)

def revoke_access(email_or_username):
    """Revoke premium access from a user."""
    
    with app.app_context():
        user = User.query.filter(
            (User.email == email_or_username) | 
            (User.username == email_or_username)
        ).first()
        
        if not user:
            print(f"❌ User not found: {email_or_username}")
            return False
        
        print(f"📧 Found user: {user.username} ({user.email})")
        
        user.subscription_status = 'free'
        user.subscription_id = None
        user.subscription_start = None
        user.subscription_end = None
        user.last_payment = None
        
        db.session.commit()
        
        print(f"✅ Access revoked for {user.username}")
        print(f"📊 New status: {user.subscription_status}")
        print(f"🎯 Profile limit: {user.get_profile_limit()}")
        
        return True

if __name__ == '__main__':
    print("🚀 AI Lesson Plan Annotator - Alpha Access Manager")
    print("=" * 60)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage examples:")
        print("  python3 grant_alpha_access.py grant cperezsanchez@dallasisd.org")
        print("  python3 grant_alpha_access.py list")
        print("  python3 grant_alpha_access.py revoke user@email.com")
        print("  python3 grant_alpha_access.py grant user@email.com 30 beta  # 30 days beta access")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'grant' and len(sys.argv) >= 3:
        email = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 365
        access_type = sys.argv[4] if len(sys.argv) > 4 else 'alpha'
        grant_alpha_access(email, days, access_type)
        
    elif command == 'list':
        list_alpha_users()
        
    elif command == 'revoke' and len(sys.argv) >= 3:
        email = sys.argv[2]
        revoke_access(email)
        
    else:
        print("❌ Invalid command. Use: grant, list, or revoke")