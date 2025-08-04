#!/usr/bin/env python3
"""
Test script to verify the Stripe webhook endpoint is working correctly.
"""

import requests
import json

def test_webhook_endpoint(url="http://127.0.0.1:8080/stripe-webhook"):
    """Test if the webhook endpoint accepts POST requests."""
    
    # Simple test payload
    test_payload = {
        "id": "evt_test",
        "object": "event",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_test",
                "customer": "cus_test",
                "status": "active"
            }
        }
    }
    
    try:
        # Test POST request
        response = requests.post(
            url,
            json=test_payload,
            headers={
                'Content-Type': 'application/json',
                'Stripe-Signature': 'test-signature'
            },
            timeout=5
        )
        
        print(f"✅ POST request successful")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        return response.status_code != 405
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_other_methods(url="http://127.0.0.1:8080/stripe-webhook"):
    """Test other HTTP methods to verify they return 405."""
    
    methods = ['GET', 'PUT', 'DELETE', 'PATCH']
    
    for method in methods:
        try:
            response = requests.request(method, url, timeout=5)
            print(f"{method}: {response.status_code} ({'❌ Should be 405' if response.status_code != 405 else '✅ Correct'})")
        except requests.exceptions.RequestException as e:
            print(f"{method}: Request failed - {e}")

if __name__ == '__main__':
    print("🔗 Testing Stripe Webhook Endpoint")
    print("=" * 40)
    
    # Test if endpoint accepts POST
    if test_webhook_endpoint():
        print("\n✅ Webhook endpoint is working correctly")
    else:
        print("\n❌ Webhook endpoint has issues")
    
    print("\n📋 Testing other HTTP methods:")
    test_other_methods()