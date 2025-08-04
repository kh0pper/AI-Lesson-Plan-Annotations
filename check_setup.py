#!/usr/bin/env python3
"""
Simple setup checker that works without dependencies installed.
Run this first to see what needs to be installed.
"""

import sys
import os

def main():
    print("🔍 AI Lesson Plan Annotator - Setup Checker")
    print("=" * 50)
    
    print(f"🐍 Python version: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("❌ ERROR: Python 3.8+ required")
        return
    
    print("\n📋 Checking files...")
    required_files = [
        'app.py', 'models.py', 'requirements.txt', 'init_db.py',
        'templates/index.html', 'templates/base.html'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (missing)")
    
    print("\n🔧 Next steps:")
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("")
    print("2. Set up environment variables:")
    print("   cp env_example.txt .env")
    print("   # Edit .env with your OpenAI API key")
    print("")
    print("3. Initialize database:")
    print("   python3 init_db.py")
    print("")
    print("4. Run the application:")
    print("   python3 app.py")
    print("")
    print("5. Visit: http://localhost:5000")
    print("")
    print("📖 For detailed instructions, see: SETUP_INSTRUCTIONS.md")

if __name__ == '__main__':
    main()