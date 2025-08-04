#!/usr/bin/env python3
"""
Test script to verify the profiles template can be rendered without BuildError.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User
from flask import render_template

def test_template_rendering():
    """Test that the profiles template renders without BuildError."""
    
    with app.app_context():
        print("🧪 Testing profiles template rendering...")
        
        try:
            # Create a mock profiles list
            mock_profiles = []
            
            # Try to render the template directly
            rendered_html = render_template('profiles.html', profiles=mock_profiles)
            
            print("✅ Profiles template renders successfully")
            
            # Check for the corrected route reference
            if 'save_profile' in rendered_html:
                print("✅ Template contains correct 'save_profile' route reference")
            
            # Check that the old incorrect reference is gone
            if 'save_current_profile' not in rendered_html:
                print("✅ Template no longer contains incorrect 'save_current_profile' reference")
            else:
                print("❌ Template still contains incorrect route reference")
                return False
            
            print(f"✅ Template rendered successfully ({len(rendered_html)} characters)")
            return True
            
        except Exception as e:
            print(f"❌ Template rendering failed: {e}")
            return False

def main():
    """Main test function."""
    print("🚀 AI Lesson Plan Annotator - Template Rendering Test")
    print("=" * 60)
    
    if test_template_rendering():
        print("\n🎉 Template rendering is working correctly!")
        print("✅ BuildError for 'save_current_profile' has been fixed")
        print("✅ Profiles page should now work when accessed via browser")
        print("\n💡 The 'Manage Profiles' link should now work without errors!")
    else:
        print("\n❌ Template rendering test failed")
        sys.exit(1)

if __name__ == '__main__':
    main()