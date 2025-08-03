#!/usr/bin/env python3
"""
Alternative server startup with different configurations.
"""

import os
from app import app

def start_server():
    """Start Flask server with multiple configuration options."""
    
    print("🚀 AI Lesson Plan Annotator - Alternative Startup")
    print("=" * 60)
    
    # Try different host/port combinations
    configs = [
        {"host": "127.0.0.1", "port": 5000},
        {"host": "localhost", "port": 5000},
        {"host": "0.0.0.0", "port": 5000},
        {"host": "127.0.0.1", "port": 8000},
        {"host": "127.0.0.1", "port": 3000},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n📍 Option {i}: http://{config['host']}:{config['port']}")
    
    print(f"\n🎯 Starting server on 127.0.0.1:5000")
    print("💡 If this doesn't work, try the URLs above manually")
    print("🌐 Access: http://127.0.0.1:5000")
    print("🌐 Alternative: http://localhost:5000")
    print("=" * 60)
    
    try:
        app.run(
            host="127.0.0.1", 
            port=5000, 
            debug=True,
            threaded=True,
            use_reloader=False  # Avoid reload issues
        )
    except OSError as e:
        print(f"\n❌ Port 5000 is busy. Error: {e}")
        print("🔄 Trying port 8000...")
        try:
            app.run(host="127.0.0.1", port=8000, debug=True)
        except Exception as e2:
            print(f"❌ Port 8000 also failed: {e2}")
            print("💡 Try running: pkill -f python  # to kill existing processes")

if __name__ == "__main__":
    start_server()