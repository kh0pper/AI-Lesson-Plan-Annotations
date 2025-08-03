#!/usr/bin/env python3
"""
Test script to verify the Flask application is working.
"""

import requests
import sys

def test_server():
    """Test if the Flask server is responding."""
    try:
        # Test main page
        response = requests.get('http://127.0.0.1:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding!")
            print(f"📍 URL: http://127.0.0.1:5000")
            print(f"📊 Status: {response.status_code}")
            print(f"📄 Content length: {len(response.content)} bytes")
            
            # Check if it contains expected content
            if b"AI Lesson Plan Annotator" in response.content:
                print("✅ Main page content looks correct!")
            else:
                print("⚠️  Main page content might have issues")
                
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://127.0.0.1:5000")
        print("💡 Make sure the Flask app is running with:")
        print("   source venv/bin/activate && python run_app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Lesson Plan Annotator Server...")
    print("=" * 50)
    
    if test_server():
        print("\n🎉 All tests passed! Your web app is ready to use.")
        print("\n🌐 Open your browser and go to: http://127.0.0.1:5000")
    else:
        print("\n💔 Server test failed.")
        sys.exit(1)