#!/usr/bin/env python3
"""
Startup script for the AI Lesson Plan Annotator web application.
"""

import os
import sys
from app import app

def main():
    print("🚀 Starting AI Lesson Plan Annotator Web Application")
    print("=" * 60)
    print("📍 Access the application at: http://localhost:5000")
    print("📁 Upload folder:", os.path.abspath(app.config['UPLOAD_FOLDER']))
    print("📁 Download folder:", os.path.abspath(app.config['DOWNLOAD_FOLDER']))
    print("=" * 60)
    print("💡 Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down the application...")
        sys.exit(0)

if __name__ == '__main__':
    main()