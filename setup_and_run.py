#!/usr/bin/env python3
"""
Setup and run script for AI Lesson Plan Annotator.
This script checks dependencies and provides setup instructions.
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'flask',
        'flask_login', 
        'flask_sqlalchemy',
        'flask_wtf',
        'stripe',
        'bcrypt',
        'openai',
        'PyPDF2',
        'reportlab',
        'pymupdf',
        'numpy',
        'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (missing)")
    
    return missing_packages

def check_environment_variables():
    """Check if required environment variables are set."""
    required_env = [
        'OPENAI_API_KEY',
        'STRIPE_SECRET_KEY', 
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_MONTHLY_PRICE_ID'
    ]
    
    missing_env = []
    
    for var in required_env:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            missing_env.append(var)
            print(f"❌ {var} (not set)")
    
    return missing_env

def initialize_database():
    """Initialize the database if it doesn't exist."""
    if not os.path.exists('ai_annotator.db'):
        print("🗄️ Initializing database...")
        try:
            from init_db import init_database
            init_database()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    else:
        print("✅ Database already exists")
    return True

def main():
    """Main setup and run function."""
    print("🚀 AI Lesson Plan Annotator - Setup & Run")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n❌ Missing {len(missing_packages)} required packages")
        print("\n🔧 To install missing dependencies, run:")
        print("   pip install -r requirements.txt")
        print("\n📝 Or install individually:")
        for package in missing_packages:
            print(f"   pip install {package}")
        print("\n⚠️ Cannot start application without required dependencies.")
        return
    
    print("\n🌍 Checking environment variables...")
    missing_env = check_environment_variables()
    
    if missing_env:
        print(f"\n⚠️ Missing {len(missing_env)} environment variables")
        print("\n🔧 Setup instructions:")
        print("1. Copy env_example.txt to .env")
        print("2. Edit .env and add your API keys:")
        for var in missing_env:
            print(f"   {var}=your_key_here")
        print("\n💡 The app can run without Stripe keys for basic functionality")
    
    print("\n🗄️ Checking database...")
    if not initialize_database():
        print("⚠️ Database setup failed, but app may still work")
    
    print("\n🚀 Starting Flask application...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Try to start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("🔧 Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == '__main__':
    main()