#!/usr/bin/env python3
"""
Test script to check billing portal functionality.
"""

from app import app
from models import db, User
from stripe_integration import StripeService

def test_billing_portal():
    """Test billing portal creation for the admin user."""
    
    with app.app_context():
        # Get the admin user
        user = User.query.filter_by(username='admin').first()
        
        if not user:
            print("❌ Admin user not found")
            return
        
        print(f"👤 Testing billing portal for user: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🆔 Stripe Customer ID: {user.stripe_customer_id}")
        print(f"📊 Subscription Status: {user.subscription_status}")
        print(f"💎 Is Premium: {user.is_premium()}")
        
        if not user.stripe_customer_id:
            print("❌ User has no Stripe customer ID - cannot create billing portal")
            return
        
        # Test billing portal creation
        return_url = "http://localhost:5001/donate"
        
        print(f"\n🔗 Creating billing portal...")
        print(f"🔄 Return URL: {return_url}")
        
        portal_session = StripeService.create_billing_portal_session(user, return_url)
        
        if portal_session:
            print(f"\n✅ SUCCESS!")
            print(f"Portal URL: {portal_session.url}")
            print(f"Session ID: {portal_session.id}")
        else:
            print(f"\n❌ FAILED - Portal session creation returned None")

if __name__ == '__main__':
    print("🧪 Testing Stripe Billing Portal")
    print("=" * 50)
    test_billing_portal()