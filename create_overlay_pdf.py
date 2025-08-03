#!/usr/bin/env python3
"""
Utility to create overlay annotated PDFs from existing JSON annotation files.
Usage: python create_overlay_pdf.py <json_file> [original_pdf]
"""

import sys
import os
from pdf_overlay_annotator import create_overlay_annotated_pdf_from_json


def main():
    if len(sys.argv) < 2:
        print("📚 Create Overlay Annotated PDF")
        print("=" * 40)
        print("Usage: python create_overlay_pdf.py <json_file> [original_pdf]")
        print("\nExamples:")
        print("  python create_overlay_pdf.py annotations_20250802_222713.json")
        print("  python create_overlay_pdf.py annotations.json fonetica8.pdf")
        print("\n🎯 Creates PDF with visual annotation overlays on the original layout")
        print("✨ Preserves original formatting with AI insights as visual overlays")
        print("📌 Perfect for maintaining document integrity while adding insights")
        return
    
    json_file = sys.argv[1]
    original_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    print(f"📄 Creating overlay annotated PDF from {json_file}...")
    print("🎯 Adding visual annotation overlays to preserve original layout")
    
    output_file = create_overlay_annotated_pdf_from_json(json_file, original_pdf)
    
    if output_file:
        print(f"✅ Overlay annotated PDF created: {output_file}")
        print("🎯 This PDF shows the original lesson plan with visual annotation overlays")
        print("📌 Annotations appear as colored boxes in the margins")
        print("✨ Perfect for maintaining original formatting while adding AI insights!")
    else:
        print("❌ Failed to create overlay annotated PDF")


if __name__ == "__main__":
    main()