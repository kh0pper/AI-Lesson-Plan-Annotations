#!/usr/bin/env python3
"""
Utility to create annotated PDFs from existing JSON annotation files.
Usage: python create_pdf_from_json.py <json_file> [original_pdf]
"""

import sys
import os
from pdf_annotator import create_annotated_pdf_from_json


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_pdf_from_json.py <json_file> [original_pdf]")
        print("\nExample:")
        print("  python create_pdf_from_json.py annotations_20250802_222713.json")
        print("  python create_pdf_from_json.py annotations_20250802_222713.json fonetica8.pdf")
        return
    
    json_file = sys.argv[1]
    original_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    print(f"📄 Creating annotated PDF from {json_file}...")
    
    output_file = create_annotated_pdf_from_json(json_file, original_pdf)
    
    if output_file:
        print(f"✅ Annotated PDF created: {output_file}")
    else:
        print("❌ Failed to create annotated PDF")


if __name__ == "__main__":
    main()