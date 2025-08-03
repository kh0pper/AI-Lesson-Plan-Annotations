#!/usr/bin/env python3
"""
Utility to create smart overlay annotated PDFs from existing JSON annotation files.
Usage: python create_smart_overlay_pdf.py <json_file> [original_pdf] [theme]
"""

import sys
import os
from smart_overlay_annotator import create_smart_overlay_pdf_from_json


def main():
    if len(sys.argv) < 2:
        print("🧠 Create Smart Overlay Annotated PDF")
        print("=" * 45)
        print("Usage: python create_smart_overlay_pdf.py <json_file> [original_pdf] [theme]")
        print("\nExamples:")
        print("  python create_smart_overlay_pdf.py annotations_20250802_222713.json")
        print("  python create_smart_overlay_pdf.py annotations.json fonetica8.pdf")
        print("  python create_smart_overlay_pdf.py annotations.json fonetica8.pdf vibrant")
        print("\n🧠 Creates PDF with INTELLIGENT annotation overlays")
        print("🎯 Features:")
        print("   • Layout-aware positioning")
        print("   • Content-relevant placement")
        print("   • Priority-based annotation hierarchy")
        print("   • Color-coded insight categories")
        print("   • Advanced white space detection")
        print("   • Customizable color themes")
        print("\n🎨 Available Themes:")
        print("   • educational (default) - Educational psychology colors")
        print("   • vibrant - High contrast colors")
        print("   • pastel - Soft, gentle colors")
        print("   • academic - Professional academic colors")
        print("   • monochrome - Grayscale for printing")
        print("   • warm - Warm, inviting colors")
        print("   • cool - Cool, calming colors")
        print("✨ The most sophisticated annotation system available!")
        return
    
    json_file = sys.argv[1]
    original_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    theme = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    print(f"📄 Creating smart overlay PDF from {json_file}...")
    if theme:
        print(f"🎨 Using '{theme}' color theme...")
    print("🧠 Analyzing layout and applying intelligent positioning...")
    
    output_file = create_smart_overlay_pdf_from_json(json_file, original_pdf, theme)
    
    if output_file:
        print(f"✅ Smart overlay PDF created: {output_file}")
        print("🎯 This PDF features:")
        print("   • Intelligent layout analysis")
        print("   • Content-aware annotation placement")
        print("   • Priority-based visual hierarchy")
        print("   • Enhanced visual design")
        print("🧠 The smartest way to annotate lesson plans!")
    else:
        print("❌ Failed to create smart overlay PDF")


if __name__ == "__main__":
    main()