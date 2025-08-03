import fitz  # PyMuPDF
import json
import re
import base64
import io
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import numpy as np


@dataclass
class SmartAnnotationBox:
    """Enhanced annotation box with intelligent positioning."""
    x: float
    y: float
    width: float
    height: float
    text: str
    annotation_type: str
    confidence: float = 1.0
    priority: int = 1
    content_relevance: str = ""
    color: Tuple[float, float, float] = (0.2, 0.4, 0.8)
    opacity: float = 0.85


class SmartOverlayAnnotator:
    """Intelligent overlay annotator with advanced placement algorithms."""
    
    def __init__(self, original_pdf_path: str):
        self.original_pdf_path = original_pdf_path
        self.doc = None
        self.page_layouts = []
        self.annotation_colors = {
            "engagement": (0.1, 0.7, 0.2),      # Vibrant green
            "differentiation": (0.9, 0.5, 0.1),  # Orange  
            "assessment": (0.5, 0.1, 0.8),       # Purple
            "improvement": (0.8, 0.1, 0.1),      # Red
            "strength": (0.1, 0.4, 0.8),         # Blue
            "resource": (0.6, 0.6, 0.1),         # Olive
            "extension": (0.8, 0.1, 0.6),        # Magenta
            "cultural": (0.1, 0.8, 0.6),         # Teal
        }
    
    def create_smart_overlay_pdf(self, annotations_data: Dict, output_filename: str = None) -> str:
        """Create PDF with intelligently placed annotation overlays."""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"smart_overlay_{timestamp}.pdf"
        
        try:
            # Open the original PDF
            self.doc = fitz.open(self.original_pdf_path)
            
            # Analyze page layouts
            print("🔍 Analyzing PDF layout and content structure...")
            self._analyze_page_layouts()
            
            # Extract and categorize annotations
            print("🧠 Processing AI annotations for intelligent placement...")
            categorized_annotations = self._categorize_annotations(annotations_data)
            
            # Generate intelligent annotation boxes
            print("📍 Calculating optimal annotation placement...")
            smart_boxes = self._generate_smart_annotation_boxes(categorized_annotations)
            
            # Apply annotations with intelligent positioning
            print("🎨 Applying smart annotation overlays...")
            self._apply_smart_annotations(smart_boxes)
            
            # Save the annotated PDF
            self.doc.save(output_filename)
            self.doc.close()
            
            return output_filename
            
        except Exception as e:
            print(f"Error creating smart overlay PDF: {e}")
            if self.doc:
                self.doc.close()
            return None
    
    def _analyze_page_layouts(self):
        """Analyze the layout of each page to identify content areas and available space."""
        self.page_layouts = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_rect = page.rect
            
            # Get text blocks and their positions
            text_blocks = page.get_text("dict")
            
            # Analyze layout
            layout_info = {
                "page_num": page_num,
                "page_rect": page_rect,
                "content_areas": self._identify_content_areas(text_blocks),
                "margins": self._calculate_margins(page_rect, text_blocks),
                "white_spaces": self._find_white_spaces(page_rect, text_blocks),
                "section_boundaries": self._identify_sections(text_blocks),
                "text_density": self._calculate_text_density(text_blocks, page_rect)
            }
            
            self.page_layouts.append(layout_info)
    
    def _identify_content_areas(self, text_blocks: Dict) -> List[Dict]:
        """Identify main content areas on the page."""
        content_areas = []
        
        if "blocks" in text_blocks:
            for block in text_blocks["blocks"]:
                if "bbox" in block and "lines" in block:
                    bbox = block["bbox"]
                    content_areas.append({
                        "type": "text_block",
                        "bbox": bbox,
                        "area": (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]),
                        "line_count": len(block["lines"])
                    })
        
        # Sort by area (largest first)
        content_areas.sort(key=lambda x: x["area"], reverse=True)
        return content_areas
    
    def _calculate_margins(self, page_rect: fitz.Rect, text_blocks: Dict) -> Dict:
        """Calculate available margin space."""
        margins = {
            "left": 50,    # Default margins
            "right": 50,
            "top": 50,
            "bottom": 50
        }
        
        if "blocks" in text_blocks:
            min_x = page_rect.width
            max_x = 0
            min_y = page_rect.height
            max_y = 0
            
            for block in text_blocks["blocks"]:
                if "bbox" in block:
                    bbox = block["bbox"]
                    min_x = min(min_x, bbox[0])
                    max_x = max(max_x, bbox[2])
                    min_y = min(min_y, bbox[1])
                    max_y = max(max_y, bbox[3])
            
            # Calculate actual margins
            margins["left"] = max(20, min_x - 10)
            margins["right"] = max(20, page_rect.width - max_x - 10)
            margins["top"] = max(20, min_y - 10)
            margins["bottom"] = max(20, page_rect.height - max_y - 10)
        
        return margins
    
    def _find_white_spaces(self, page_rect: fitz.Rect, text_blocks: Dict) -> List[Dict]:
        """Find available white space areas for annotations."""
        white_spaces = []
        
        # Check right margin
        margins = self._calculate_margins(page_rect, text_blocks)
        if margins["right"] > 100:  # Enough space for annotations
            white_spaces.append({
                "type": "right_margin",
                "x": page_rect.width - margins["right"],
                "y": 80,
                "width": margins["right"] - 20,
                "height": page_rect.height - 160,
                "priority": 1
            })
        
        # Check left margin
        if margins["left"] > 100:
            white_spaces.append({
                "type": "left_margin", 
                "x": 10,
                "y": 80,
                "width": margins["left"] - 20,
                "height": page_rect.height - 160,
                "priority": 2
            })
        
        # Check top area
        if margins["top"] > 60:
            white_spaces.append({
                "type": "top_area",
                "x": margins["left"],
                "y": 10,
                "width": page_rect.width - margins["left"] - margins["right"],
                "height": margins["top"] - 20,
                "priority": 3
            })
        
        return white_spaces
    
    def _identify_sections(self, text_blocks: Dict) -> List[Dict]:
        """Identify lesson plan sections for content-aware placement."""
        sections = []
        
        if "blocks" not in text_blocks:
            return sections
        
        section_keywords = {
            "objectives": ["objetivos", "objectives", "objetivo"],
            "materials": ["materiales", "materials", "material"],
            "activities": ["actividad", "activity", "nosotros", "leemos"],
            "assessment": ["evaluación", "assessment", "compartir", "reflexionar"]
        }
        
        for block in text_blocks["blocks"]:
            if "lines" in block and "bbox" in block:
                block_text = ""
                for line in block["lines"]:
                    if "spans" in line:
                        for span in line["spans"]:
                            if "text" in span:
                                block_text += span["text"].lower() + " "
                
                # Check for section keywords
                for section_type, keywords in section_keywords.items():
                    if any(keyword in block_text for keyword in keywords):
                        sections.append({
                            "type": section_type,
                            "bbox": block["bbox"],
                            "text_sample": block_text[:100]
                        })
                        break
        
        return sections
    
    def _calculate_text_density(self, text_blocks: Dict, page_rect: fitz.Rect) -> float:
        """Calculate text density on the page."""
        if "blocks" not in text_blocks:
            return 0.0
        
        total_text_area = 0
        for block in text_blocks["blocks"]:
            if "bbox" in block:
                bbox = block["bbox"]
                total_text_area += (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        
        page_area = page_rect.width * page_rect.height
        return total_text_area / page_area if page_area > 0 else 0.0
    
    def _categorize_annotations(self, annotations_data: Dict) -> Dict:
        """Categorize and prioritize annotations for intelligent placement."""
        if 'annotations' not in annotations_data:
            return {}
        
        annotation_text = annotations_data['annotations']
        
        categorized = {
            "high_priority": {
                "engagement": self._extract_annotation_points(annotation_text, "Student Engagement"),
                "improvement": self._extract_annotation_points(annotation_text, "Areas for Improvement")
            },
            "medium_priority": {
                "differentiation": self._extract_annotation_points(annotation_text, "Differentiation"),
                "assessment": self._extract_annotation_points(annotation_text, "Assessment")
            },
            "low_priority": {
                "strength": self._extract_annotation_points(annotation_text, "Pedagogical Strengths"),
                "resource": self._extract_annotation_points(annotation_text, "Resource Optimization"),
                "extension": self._extract_annotation_points(annotation_text, "Extension Activities"),
                "cultural": self._extract_annotation_points(annotation_text, "Cultural")
            }
        }
        
        return categorized
    
    def _extract_annotation_points(self, text: str, section_name: str) -> List[str]:
        """Extract specific bullet points from annotation sections."""
        lines = text.split('\n')
        in_section = False
        points = []
        
        for line in lines:
            line = line.strip()
            
            if section_name.lower() in line.lower() and ('**' in line or '##' in line):
                in_section = True
                continue
            elif in_section and ('**' in line or '##' in line) and section_name.lower() not in line.lower():
                break
            elif in_section and line:
                clean_line = line.replace('*', '').replace('#', '').replace('-', '').strip()
                if clean_line and len(clean_line) > 15:
                    # Truncate for overlay display
                    if len(clean_line) > 70:
                        clean_line = clean_line[:67] + "..."
                    points.append(clean_line)
        
        return points[:2]  # Limit to top 2 per category
    
    def _generate_smart_annotation_boxes(self, categorized_annotations: Dict) -> List[SmartAnnotationBox]:
        """Generate intelligently positioned annotation boxes."""
        smart_boxes = []
        
        for page_num, layout in enumerate(self.page_layouts):
            page_boxes = self._generate_page_annotations(page_num, layout, categorized_annotations)
            smart_boxes.extend(page_boxes)
        
        return smart_boxes
    
    def _generate_page_annotations(self, page_num: int, layout: Dict, annotations: Dict) -> List[SmartAnnotationBox]:
        """Generate annotations for a specific page."""
        boxes = []
        white_spaces = layout["white_spaces"]
        sections = layout["section_boundaries"]
        
        if not white_spaces:
            return boxes
        
        # Use the best available white space (highest priority)
        primary_space = sorted(white_spaces, key=lambda x: x["priority"])[0]
        
        # Calculate annotation placement
        box_height = 65
        box_width = min(primary_space["width"] - 10, 160)
        spacing = 75
        start_y = primary_space["y"] + 20
        
        current_y = start_y
        annotations_placed = 0
        max_annotations = int((primary_space["height"] - 40) / spacing)
        
        # Place high priority annotations first
        for priority_level in ["high_priority", "medium_priority", "low_priority"]:
            if annotations_placed >= max_annotations:
                break
                
            for ann_type, ann_list in annotations.get(priority_level, {}).items():
                if annotations_placed >= max_annotations:
                    break
                    
                for annotation_text in ann_list:
                    if annotations_placed >= max_annotations:
                        break
                    
                    # Create smart annotation box
                    box = SmartAnnotationBox(
                        x=primary_space["x"] + 5,
                        y=current_y,
                        width=box_width,
                        height=box_height,
                        text=annotation_text,
                        annotation_type=ann_type,
                        content_relevance=self._find_content_relevance(ann_type, sections),
                        color=self.annotation_colors.get(ann_type, (0.5, 0.5, 0.5)),
                        priority=1 if priority_level == "high_priority" else 
                                2 if priority_level == "medium_priority" else 3
                    )
                    
                    boxes.append(box)
                    current_y += spacing
                    annotations_placed += 1
        
        return boxes
    
    def _find_content_relevance(self, annotation_type: str, sections: List[Dict]) -> str:
        """Find which content section this annotation is most relevant to."""
        relevance_map = {
            "engagement": "objectives",
            "differentiation": "activities", 
            "assessment": "assessment",
            "improvement": "activities",
            "strength": "objectives",
            "resource": "materials"
        }
        
        relevant_section = relevance_map.get(annotation_type, "general")
        
        # Check if we have this section on the page
        for section in sections:
            if section["type"] == relevant_section:
                return f"Related to {section['type']} section"
        
        return "General insight"
    
    def _apply_smart_annotations(self, smart_boxes: List[SmartAnnotationBox]):
        """Apply smart annotation boxes to the PDF."""
        
        # Group boxes by page
        page_boxes = {}
        for box in smart_boxes:
            page_num = 0  # Default to first page - could be enhanced
            if page_num not in page_boxes:
                page_boxes[page_num] = []
            page_boxes[page_num].append(box)
        
        # Apply annotations to each page
        for page_num, boxes in page_boxes.items():
            if page_num < len(self.doc):
                page = self.doc[page_num]
                
                for box in boxes:
                    self._add_smart_annotation_box(page, box)
    
    def _add_smart_annotation_box(self, page, box: SmartAnnotationBox):
        """Add a smart annotation box to the page."""
        
        # Create main annotation rectangle
        rect = fitz.Rect(box.x, box.y, box.x + box.width, box.y + box.height)
        
        # Add colored background with enhanced visual appeal
        page.draw_rect(rect, color=box.color, fill=box.color, width=0)
        
        # Add gradient effect (simulate with overlapping rectangles)
        for i in range(3):
            inner_rect = fitz.Rect(
                box.x + i, box.y + i, 
                box.x + box.width - i, box.y + box.height - i
            )
            alpha = 0.3 - (i * 0.1)
            lighter_color = tuple(min(1.0, c + alpha) for c in box.color)
            page.draw_rect(inner_rect, color=lighter_color, fill=lighter_color, width=0)
        
        # Add white background for text
        text_rect = fitz.Rect(box.x + 4, box.y + 4, box.x + box.width - 4, box.y + box.height - 4)
        page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
        
        # Add border with priority-based thickness
        border_width = box.priority  # Thicker border for higher priority
        page.draw_rect(rect, color=box.color, fill=None, width=border_width)
        
        # Add annotation type icon and text
        icon = self._get_smart_annotation_icon(box.annotation_type)
        display_text = f"{icon} {box.text}"
        
        self._add_smart_text(page, display_text, text_rect, box.priority)
    
    def _get_smart_annotation_icon(self, annotation_type: str) -> str:
        """Get contextual icon for annotation type."""
        icons = {
            "engagement": "🚀",     # Rocket for engagement
            "assessment": "📈",     # Chart for assessment
            "differentiation": "🎯", # Target for differentiation
            "strength": "💪",       # Muscle for strengths
            "improvement": "🔧",    # Wrench for improvements
            "resource": "🎒",       # Backpack for resources
            "extension": "⭐",      # Star for extensions
            "cultural": "🌍"        # Globe for cultural
        }
        return icons.get(annotation_type, "💡")
    
    def _add_smart_text(self, page, text: str, rect: fitz.Rect, priority: int):
        """Add intelligently formatted text to annotation box."""
        
        # Adjust font size based on priority
        font_size = 8 if priority == 1 else 7 if priority == 2 else 6
        
        # Word wrap
        words = text.split()
        lines = []
        current_line = ""
        max_chars_per_line = int((rect.width - 10) / (font_size * 0.6))
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Add lines with smart spacing
        line_height = font_size + 2
        y_offset = 10
        
        for i, line in enumerate(lines[:4]):  # Max 4 lines
            if y_offset + line_height > rect.height - 5:
                break
            
            text_point = fitz.Point(rect.x0 + 6, rect.y0 + y_offset)
            
            # Bold for first line (icon + beginning)
            font_name = "hebo" if i == 0 else "helv"  # Bold for first line
            
            page.insert_text(
                text_point,
                line,
                fontsize=font_size,
                color=(0.1, 0.1, 0.1),  # Dark gray instead of black
                fontname=font_name
            )
            y_offset += line_height


def create_smart_overlay_pdf_from_json(json_file: str, original_pdf: str = None) -> str:
    """Create smart overlay PDF from saved JSON results."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            annotations_data = json.load(f)
        
        if original_pdf is None:
            original_pdf = annotations_data.get('lesson_info', {}).get('pdf_path', 'fonetica8.pdf')
        
        generator = SmartOverlayAnnotator(original_pdf)
        output_file = generator.create_smart_overlay_pdf(annotations_data)
        
        return output_file
        
    except Exception as e:
        print(f"Error creating smart overlay PDF from JSON: {e}")
        return None