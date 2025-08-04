#!/usr/bin/env python3
"""
Test the webhook with real Stripe event data from the CLI trigger.
"""

import requests
import json

def test_real_webhook():
    """Test webhook with actual Stripe event data."""
    
    # This is the actual event structure from stripe trigger command
    webhook_data = {
        "id": "evt_test_webhook",
        "object": "event",
        "api_version": "2024-12-18.acacia",
        "created": 1754314814,
        "data": {
            "object": {
                "id": "sub_test123",
                "object": "subscription",
                "customer": "cus_So0dHqH1N7Nokb",  # Your actual customer ID
                "status": "active",
                "current_period_end": 1756993210,
                "current_period_start": 1754314810,
                "items": {
                    "data": [{
                        "price": {
                            "id": "price_1RsOVWG4wBb8On8f4EN5nXzt",
                            "unit_amount": 500,
                            "currency": "usd"
                        }
                    }]
                }
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "type": "customer.subscription.created"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/stripe-webhook",
            json=webhook_data,
            headers={
                'Content-Type': 'application/json',
                'Stripe-Signature': 'test-signature'
            },
            timeout=10
        )
        
        print(f"✅ Webhook test completed")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("🎉 Webhook processed successfully!")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == '__main__':
    print("🔗 Testing Real Stripe Webhook Data")
    print("=" * 40)
    test_real_webhook()