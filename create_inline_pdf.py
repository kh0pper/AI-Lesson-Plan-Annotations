#!/usr/bin/env python3
"""
Utility to create inline annotated PDFs from existing JSON annotation files.
Usage: python create_inline_pdf.py <json_file> [original_pdf]
"""

import sys
import os
from inline_pdf_annotator import create_inline_annotated_pdf_from_json


def main():
    if len(sys.argv) < 2:
        print("📚 Create Inline Annotated PDF")
        print("=" * 40)
        print("Usage: python create_inline_pdf.py <json_file> [original_pdf]")
        print("\nExamples:")
        print("  python create_inline_pdf.py annotations_20250802_222713.json")
        print("  python create_inline_pdf.py annotations.json fonetica8.pdf")
        print("\n✨ Creates PDF with annotations placed inline alongside lesson content")
        print("🎯 Better for reading and immediate implementation")
        return
    
    json_file = sys.argv[1]
    original_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    print(f"📄 Creating inline annotated PDF from {json_file}...")
    print("✨ Annotations will be placed alongside lesson content")
    
    output_file = create_inline_annotated_pdf_from_json(json_file, original_pdf)
    
    if output_file:
        print(f"✅ Inline annotated PDF created: {output_file}")
        print("🎯 This PDF shows annotations directly next to relevant lesson sections")
        print("📚 Perfect for immediate classroom implementation!")
    else:
        print("❌ Failed to create inline annotated PDF")


if __name__ == "__main__":
    main()