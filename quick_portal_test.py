#!/usr/bin/env python3
"""
Quick test for billing portal after Stripe configuration.
"""

import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_stripe_portal_config():
    """Test if Stripe portal is configured."""
    
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    try:
        # Try to create a billing portal session with a real customer
        portal_session = stripe.billing_portal.Session.create(
            customer='cus_So0dHqH1N7Nokb',  # Your actual customer ID
            return_url='http://localhost:5001/donate',
        )
        
        print("✅ SUCCESS! Portal session created")
        print(f"Portal URL: {portal_session.url}")
        print(f"Session ID: {portal_session.id}")
        return True
        
    except stripe.error.InvalidRequestError as e:
        if "No configuration provided" in str(e):
            print("❌ Customer Portal not configured yet")
            print("🔗 Configure at: https://dashboard.stripe.com/settings/billing/portal")
            return False
        else:
            print(f"❌ Other error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Quick Billing Portal Test")
    print("=" * 30)
    test_stripe_portal_config()