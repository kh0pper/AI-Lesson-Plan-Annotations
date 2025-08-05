#!/usr/bin/env python3
"""
Test script for Gift Card API integration with Teachers Pay Teachers.

This script demonstrates how Teachers Pay Teachers would integrate 
with the gift card generation API.
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:5001"  # Change to your deployment URL
API_KEY = "tpt-gift-card-key-2025"  # This should match TPT_API_KEY env var

def test_gift_card_generation():
    """Test the gift card generation API endpoint."""
    
    print("🎁 Testing Gift Card Generation API")
    print("=" * 50)
    
    # Test data (simulating Teachers Pay Teachers purchase)
    test_data = {
        "purchase_id": "TPT-ORDER-12345",
        "purchase_email": "teacher@school.edu",
        "value_months": 1,
        "expires_days": 365,
        "notes": "Teachers Pay Teachers purchase - Premium 1 Month Gift Card"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/gift-cards/generate",
            headers={
                "Content-Type": "application/json",
                "API-Key": API_KEY
            },
            json=test_data
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Gift Card Code: {result['gift_card']['code']}")
            print(f"Value: {result['gift_card']['value_months']} month(s)")
            print(f"Purchase ID: {result['gift_card']['purchase_id']}")
            print(f"Created: {result['gift_card']['created_at']}")
            
            if result['gift_card']['expires_at']:
                print(f"Expires: {result['gift_card']['expires_at']}")
            
            return result['gift_card']['code']
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("Make sure the Flask app is running on http://localhost:5001")
        print("Run: python3 app.py")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


def test_gift_card_validation(code):
    """Test the gift card validation API endpoint."""
    
    print("\n🔍 Testing Gift Card Validation API")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/gift-cards/validate",
            headers={"Content-Type": "application/json"},
            json={"code": code}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Valid: {result['valid']}")
            print(f"Message: {result['message']}")
            
            if result['valid']:
                print(f"Value: {result['value_months']} month(s)")
                if result['expires_at']:
                    print(f"Expires: {result['expires_at']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_invalid_api_key():
    """Test API security with invalid API key."""
    
    print("\n🔒 Testing API Security (Invalid Key)")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/gift-cards/generate",
            headers={
                "Content-Type": "application/json",
                "API-Key": "invalid-key"
            },
            json={"purchase_id": "test"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Security working correctly - Invalid API key rejected")
        else:
            print("❌ Security issue - Invalid key was accepted!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    print("Teachers Pay Teachers Gift Card API Integration Test")
    print("=" * 60)
    
    # Test 1: Generate a gift card
    gift_card_code = test_gift_card_generation()
    
    # Test 2: Validate the generated gift card
    if gift_card_code:
        test_gift_card_validation(gift_card_code)
    
    # Test 3: Test API security
    test_invalid_api_key()
    
    print("\n📋 Integration Summary:")
    print("=" * 30)
    print("1. Teachers Pay Teachers calls /api/gift-cards/generate after purchase")
    print("2. API returns unique gift card code")
    print("3. TPT delivers code to customer")
    print("4. Customer redeems code at /gift-cards/redeem")
    print("5. System grants premium access automatically")
    
    print("\n🔧 Required Environment Variables:")
    print("- TPT_API_KEY: API key for Teachers Pay Teachers integration")
    print("- Set in production deployment or .env file")
    
    print("\nTest completed! 🎉")