import fitz  # PyMuPDF
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AnnotationBox:
    """Represents an annotation overlay box."""
    x: float
    y: float
    width: float
    height: float
    text: str
    annotation_type: str
    color: Tuple[float, float, float] = (0.2, 0.4, 0.8)  # Blue
    opacity: float = 0.85


class PDFOverlayAnnotator:
    """Create PDF annotations as visual overlays on the original document."""
    
    def __init__(self, original_pdf_path: str):
        self.original_pdf_path = original_pdf_path
        self.doc = None
        self.annotations = {}
        self.annotation_colors = {
            "engagement": (0.2, 0.6, 0.2),      # Green
            "differentiation": (0.8, 0.4, 0.2),  # Orange  
            "assessment": (0.6, 0.2, 0.8),       # Purple
            "improvement": (0.8, 0.2, 0.2),      # Red
            "strength": (0.2, 0.4, 0.8),         # Blue
            "resource": (0.6, 0.6, 0.2),         # Olive
            "extension": (0.8, 0.2, 0.6),        # Pink
            "cultural": (0.2, 0.8, 0.6),         # Teal
        }
    
    def create_overlay_annotated_pdf(self, annotations_data: Dict, output_filename: str = None) -> str:
        """Create PDF with annotation overlays on the original document."""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"overlay_annotated_lesson_{timestamp}.pdf"
        
        try:
            # Open the original PDF
            self.doc = fitz.open(self.original_pdf_path)
            self.annotations = annotations_data
            
            # Analyze content and generate annotation positions
            annotation_boxes = self._generate_annotation_boxes()
            
            # Add annotations to PDF
            self._add_annotation_overlays(annotation_boxes)
            
            # Save the annotated PDF
            self.doc.save(output_filename)
            self.doc.close()
            
            return output_filename
            
        except Exception as e:
            print(f"Error creating overlay annotated PDF: {e}")
            if self.doc:
                self.doc.close()
            return None
    
    def _generate_annotation_boxes(self) -> List[AnnotationBox]:
        """Generate annotation boxes with smart positioning."""
        annotation_boxes = []
        
        if 'annotations' not in self.annotations:
            return annotation_boxes
        
        # Parse AI annotations
        parsed_annotations = self._parse_ai_annotations()
        
        # Process each page
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_rect = page.rect
            
            # Get text blocks from the page
            text_blocks = page.get_text("dict")
            
            # Find annotation opportunities on this page
            page_annotations = self._find_annotation_positions(
                page, text_blocks, parsed_annotations, page_num
            )
            
            annotation_boxes.extend(page_annotations)
        
        return annotation_boxes
    
    def _parse_ai_annotations(self) -> Dict[str, List[str]]:
        """Parse AI annotations into categorized insights."""
        if 'annotations' not in self.annotations:
            return {}
        
        annotation_text = self.annotations['annotations']
        
        parsed = {
            "strengths": self._extract_bullet_points(annotation_text, "Pedagogical Strengths"),
            "engagement": self._extract_bullet_points(annotation_text, "Student Engagement"),
            "assessment": self._extract_bullet_points(annotation_text, "Assessment"),
            "differentiation": self._extract_bullet_points(annotation_text, "Differentiation"),
            "improvement": self._extract_bullet_points(annotation_text, "Areas for Improvement"),
            "resources": self._extract_bullet_points(annotation_text, "Resource Optimization"),
            "extension": self._extract_bullet_points(annotation_text, "Extension Activities"),
            "cultural": self._extract_bullet_points(annotation_text, "Cultural")
        }
        
        return parsed
    
    def _extract_bullet_points(self, text: str, section_name: str) -> List[str]:
        """Extract bullet points from a specific section."""
        lines = text.split('\n')
        in_section = False
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            
            if section_name.lower() in line.lower() and ('**' in line or '##' in line):
                in_section = True
                continue
            elif in_section and ('**' in line or '##' in line) and section_name.lower() not in line.lower():
                break
            elif in_section and line:
                # Clean bullet point
                clean_line = line.replace('*', '').replace('#', '').replace('-', '').strip()
                if clean_line and len(clean_line) > 10:
                    # Truncate for overlay display
                    if len(clean_line) > 80:
                        clean_line = clean_line[:77] + "..."
                    bullet_points.append(clean_line)
        
        return bullet_points[:2]  # Limit to 2 per section for space
    
    def _find_annotation_positions(self, page, text_blocks: Dict, annotations: Dict, page_num: int) -> List[AnnotationBox]:
        """Find smart positions for annotations on a page."""
        boxes = []
        page_rect = page.rect
        
        # Get text content for keyword matching
        page_text = page.get_text().lower()
        
        # Keywords that suggest different annotation types
        keyword_mapping = {
            "objectives": ("engagement", "💡 Engagement Boost"),
            "objetivos": ("engagement", "💡 Engagement Boost"),
            "materials": ("resources", "🔧 Resource Tip"),
            "materiales": ("resources", "🔧 Resource Tip"), 
            "actividad": ("differentiation", "🎯 Differentiation"),
            "activity": ("differentiation", "🎯 Differentiation"),
            "evaluación": ("assessment", "📊 Assessment Idea"),
            "assessment": ("assessment", "📊 Assessment Idea"),
            "phonological": ("strengths", "⭐ Strength"),
            "fonológica": ("strengths", "⭐ Strength"),
        }
        
        # Find available annotation space (margins)
        margin_width = 150
        annotation_height = 60
        right_margin_x = page_rect.width - margin_width
        
        # Position annotations based on content
        y_position = 100  # Start position
        spacing = 80
        
        # Add annotations based on keywords found
        annotations_added = 0
        max_annotations_per_page = 4
        
        for keyword, (annotation_type, prefix) in keyword_mapping.items():
            if keyword in page_text and annotations_added < max_annotations_per_page:
                insights = annotations.get(annotation_type, [])
                if insights:
                    # Take first available insight
                    insight_text = f"{prefix}: {insights[0]}"
                    
                    # Create annotation box in right margin
                    box = AnnotationBox(
                        x=right_margin_x,
                        y=y_position,
                        width=margin_width - 10,
                        height=annotation_height,
                        text=insight_text,
                        annotation_type=annotation_type,
                        color=self.annotation_colors.get(annotation_type, (0.2, 0.4, 0.8))
                    )
                    boxes.append(box)
                    
                    y_position += spacing
                    annotations_added += 1
        
        # Add general improvement suggestion if space available
        if annotations_added < max_annotations_per_page and annotations.get("improvement"):
            improvement_text = f"🔧 Tip: {annotations['improvement'][0]}"
            box = AnnotationBox(
                x=right_margin_x,
                y=y_position,
                width=margin_width - 10,
                height=annotation_height,
                text=improvement_text,
                annotation_type="improvement",
                color=self.annotation_colors["improvement"]
            )
            boxes.append(box)
        
        return boxes
    
    def _add_annotation_overlays(self, annotation_boxes: List[AnnotationBox]):
        """Add annotation overlays to the PDF."""
        
        for box in annotation_boxes:
            # Find the appropriate page for this annotation
            page_num = 0  # Default to first page, could be improved with better positioning logic
            if page_num < len(self.doc):
                page = self.doc[page_num]
                
                # Create annotation rectangle
                rect = fitz.Rect(box.x, box.y, box.x + box.width, box.y + box.height)
                
                # Add colored background rectangle
                page.draw_rect(rect, color=box.color, fill=box.color, width=0)
                
                # Add semi-transparent white background for text readability
                text_rect = fitz.Rect(box.x + 2, box.y + 2, box.x + box.width - 2, box.y + box.height - 2)
                page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
                
                # Add border
                page.draw_rect(rect, color=box.color, fill=None, width=1)
                
                # Add text
                self._add_text_to_box(page, box)
    
    def _add_text_to_box(self, page, box: AnnotationBox):
        """Add wrapped text to an annotation box."""
        # Calculate text area
        text_rect = fitz.Rect(box.x + 5, box.y + 5, box.x + box.width - 5, box.y + box.height - 5)
        
        # Split text into lines that fit
        words = box.text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) * 6 < box.width - 10:  # Rough character width estimation
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Add lines to PDF
        font_size = 8
        line_height = 10
        y_offset = 0
        
        for i, line in enumerate(lines[:4]):  # Limit to 4 lines
            if y_offset + line_height > box.height - 10:
                break
                
            text_point = fitz.Point(box.x + 5, box.y + 15 + y_offset)
            page.insert_text(
                text_point,
                line,
                fontsize=font_size,
                color=(0, 0, 0),  # Black text
                fontname="helv"
            )
            y_offset += line_height
    
    def _distribute_annotations_across_pages(self, annotation_boxes: List[AnnotationBox]):
        """Distribute annotations across multiple pages if needed."""
        # This could be enhanced to better distribute annotations
        # based on content relevance and available space
        
        annotations_per_page = 3
        for i, box in enumerate(annotation_boxes):
            target_page = min(i // annotations_per_page, len(self.doc) - 1)
            # Could adjust y position based on page and annotation index
            pass


def create_overlay_annotated_pdf_from_json(json_file: str, original_pdf: str = None) -> str:
    """Create overlay annotated PDF from saved JSON results."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            annotations_data = json.load(f)
        
        if original_pdf is None:
            original_pdf = annotations_data.get('lesson_info', {}).get('pdf_path', 'fonetica8.pdf')
        
        generator = PDFOverlayAnnotator(original_pdf)
        output_file = generator.create_overlay_annotated_pdf(annotations_data)
        
        return output_file
        
    except Exception as e:
        print(f"Error creating overlay annotated PDF from JSON: {e}")
        return None