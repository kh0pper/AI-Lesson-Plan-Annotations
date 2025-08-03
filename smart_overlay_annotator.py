import fitz  # PyMuPDF
import json
import re
import base64
import io
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from multimodal_ai_client import MultimodalLlamaClient


@dataclass
class ContentHighlight:
    """Represents highlighted content that relates to an annotation."""
    x: float
    y: float
    width: float
    height: float
    text_content: str
    highlight_color: Tuple[float, float, float]
    annotation_type: str


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
    related_highlights: List[ContentHighlight] = None
    target_content_area: Tuple[float, float, float, float] = None  # (x, y, width, height)


class SmartOverlayAnnotator:
    """Intelligent overlay annotator with advanced placement algorithms."""
    
    def __init__(self, original_pdf_path: str, theme: str = None):
        self.original_pdf_path = original_pdf_path
        self.doc = None
        self.page_layouts = []
        self.multimodal_client = MultimodalLlamaClient()
        self.annotation_colors = self._load_theme_colors(theme)
    
    def _load_theme_colors(self, theme: str = None) -> Dict[str, Tuple[float, float, float]]:
        """Load color scheme from themes.json file."""
        try:
            themes_path = os.path.join(os.path.dirname(__file__), 'themes.json')
            with open(themes_path, 'r') as f:
                themes_data = json.load(f)
            
            # Use specified theme or default
            if theme is None:
                theme = themes_data.get('default_theme', 'educational')
            
            if theme not in themes_data['themes']:
                print(f"⚠️ Theme '{theme}' not found, using 'educational' theme")
                theme = 'educational'
            
            colors = themes_data['themes'][theme]['colors']
            # Convert lists to tuples for compatibility
            return {k: tuple(v) for k, v in colors.items()}
            
        except Exception as e:
            print(f"⚠️ Error loading themes: {e}, using default colors")
            # Fallback to default colors
            return {
                "engagement": (0.1, 0.7, 0.2),
                "differentiation": (0.9, 0.5, 0.1),
                "assessment": (0.5, 0.1, 0.8),
                "improvement": (0.8, 0.1, 0.1),
                "strength": (0.1, 0.4, 0.8),
                "resource": (0.6, 0.6, 0.1),
                "extension": (0.8, 0.1, 0.6),
                "cultural": (0.1, 0.8, 0.6),
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
            # Get parameters from annotations_data for custom category support
            parameters = annotations_data.get('parameters_used', {})
            categorized_annotations = self._categorize_annotations(annotations_data, parameters)
            
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
        
        # More flexible right margin check
        if margins["right"] > 60:  # Reduced requirement
            white_spaces.append({
                "type": "right_margin",
                "x": page_rect.width - margins["right"] + 10,
                "y": 80,
                "width": max(150, margins["right"] - 30),  # Increased minimum width
                "height": page_rect.height - 160,
                "priority": 1
            })
        
        # Check left margin  
        if margins["left"] > 60:  # Reduced requirement
            white_spaces.append({
                "type": "left_margin", 
                "x": 10,
                "y": 80,
                "width": max(150, margins["left"] - 30),  # Increased minimum width
                "height": page_rect.height - 160,
                "priority": 2
            })
        
        # Check top area
        if margins["top"] > 40:  # Reduced requirement
            white_spaces.append({
                "type": "top_area",
                "x": margins["left"],
                "y": 10,
                "width": page_rect.width - margins["left"] - margins["right"],
                "height": max(50, margins["top"] - 20),
                "priority": 3
            })
        
        # Fallback: create wider overlay areas with better positioning
        if not white_spaces:
            # Primary wide area on the right
            white_spaces.append({
                "type": "right_overlay",
                "x": page_rect.width - 200,  # Wider area: 200pt from right edge
                "y": 80,
                "width": 180,  # Increased width from 120 to 180
                "height": page_rect.height - 160,
                "priority": 1
            })
            
            # Secondary area on the left if page is wide enough
            if page_rect.width > 500:  # Only for wide pages
                white_spaces.append({
                    "type": "left_overlay",
                    "x": 20,
                    "y": 80,
                    "width": 180,
                    "height": page_rect.height - 160,
                    "priority": 2
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
    
    def _categorize_annotations(self, annotations_data: Dict, parameters: Dict = None) -> Dict:
        """Categorize and prioritize annotations for intelligent placement."""
        if 'annotations' not in annotations_data:
            return {}
        
        annotation_text = annotations_data['annotations']
        
        # Check if using custom category definitions
        if parameters and 'custom_category_definitions' in parameters:
            return self._categorize_custom_annotations(annotation_text, parameters['custom_category_definitions'])
        
        # Use default categorization with both English and Spanish section headers
        categorized = {
            "high_priority": {
                "engagement": self._extract_annotation_points(annotation_text, ["Student Engagement Opportunities", "Oportunidades para la participación de los estudiantes", "participación de los estudiantes"]),
                "improvement": self._extract_annotation_points(annotation_text, ["Areas for Improvement", "Áreas de mejora", "mejora"])
            },
            "medium_priority": {
                "differentiation": self._extract_annotation_points(annotation_text, ["Differentiation Strategies", "Estrategias de diferenciación", "diferenciación"]),
                "assessment": self._extract_annotation_points(annotation_text, ["Assessment Suggestions", "Sugerencias de evaluación", "evaluación"])
            },
            "low_priority": {
                "strength": self._extract_annotation_points(annotation_text, ["Pedagogical Strengths", "Fortalezas pedagógicas", "Fortalezas"]),
                "resource": self._extract_annotation_points(annotation_text, ["Resource Optimization", "Optimización de recursos", "recursos"]),
                "extension": self._extract_annotation_points(annotation_text, ["Extension Activities", "Actividades de extensión", "extensión"]),
                "cultural": self._extract_annotation_points(annotation_text, ["Cultural/Linguistic Considerations", "Consideraciones culturales/lingüísticas", "culturales"])
            }
        }
        
        return categorized
    
    def _categorize_custom_annotations(self, annotation_text: str, custom_definitions: Dict) -> Dict:
        """Categorize annotations using user-defined category meanings."""
        categorized = {
            "high_priority": {},
            "medium_priority": {},
            "low_priority": {}
        }
        
        # Map custom categories to priorities (first 2 = high, next 3 = medium, rest = low)
        category_keys = list(custom_definitions.keys())
        
        for i, (category_key, definition) in enumerate(custom_definitions.items()):
            # Extract annotations based on the user-defined meaning
            # Match the actual AI output format: ### 1. **Definition** (Spanish translation)
            search_terms = [
                f"### {i+1}. **{definition}**",  # Exact AI format
                f"{i+1}. **{definition}**",      # Without ###
                f"**{definition}**",             # Just the bold definition
                definition,                       # Plain definition
                definition.lower(),               # Lowercase
                definition.upper()                # Uppercase
            ]
            
            extracted_points = self._extract_annotation_points(annotation_text, search_terms)
            
            # Assign priority based on order (first categories are higher priority)
            if i < 2:  # First 2 categories = high priority
                categorized["high_priority"][category_key] = extracted_points
            elif i < 5:  # Next 3 categories = medium priority  
                categorized["medium_priority"][category_key] = extracted_points
            else:  # Remaining categories = low priority
                categorized["low_priority"][category_key] = extracted_points
        
        return categorized
    
    def _extract_annotation_points(self, text: str, section_names) -> List[str]:
        """Extract specific bullet points from annotation sections."""
        # Handle both single string and list of section names
        if isinstance(section_names, str):
            section_names = [section_names]
            
        lines = text.split('\n')
        in_section = False
        points = []
        
        for line in lines:
            line = line.strip()
            
            # Check if we're entering any of the target sections
            section_found = False
            for section_name in section_names:
                if section_name.lower() in line.lower() and ('**' in line or '##' in line or '*' in line):
                    in_section = True
                    section_found = True
                    break
            
            if section_found:
                continue
                
            # Check if we're entering a new section (exit current)
            # Only exit if it's a proper section header (starts with ### or is numbered like "2. **")
            elif in_section and (line.startswith('###') or (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')) and '**' in line)) and not any(sn.lower() in line.lower() for sn in section_names):
                break
            # Extract bullet points and detailed content
            elif in_section and line:
                # Skip intro/connecting sentences
                if line.startswith(('To enhance', 'To accommodate', 'For formative', 'For summative', 'To better', 'To deepen')):
                    continue
                
                # Extract bullet points (starting with -, *, or •)
                if line.startswith(('-', '*', '•')):
                    clean_line = line.replace('*', '').replace('#', '').replace('-', '').replace('•', '').strip()
                    
                    # Extract just the main concept before colon
                    if ':' in clean_line:
                        main_concept = clean_line.split(':')[0].strip()
                        detail = clean_line.split(':', 1)[1].strip()
                        # Use the detail if it's not too long, otherwise use concept
                        if len(detail) <= 60:
                            clean_line = detail
                        else:
                            clean_line = main_concept
                    
                    if clean_line and len(clean_line) > 10:
                        # No truncation needed with expandable boxes
                        points.append(clean_line)
                
                # Also extract standalone important lines (like recommendations)
                elif len(line) > 20 and not line.endswith(':') and '**' not in line:
                    clean_line = line.replace('*', '').strip()
                    # No truncation needed with expandable boxes
                    points.append(clean_line)
        
        return points[:3]  # Limit to top 3 per category
    
    def _generate_smart_annotation_boxes(self, categorized_annotations: Dict) -> List[SmartAnnotationBox]:
        """Generate intelligently positioned annotation boxes."""
        smart_boxes = []
        
        # Distribute annotations across all pages
        all_annotations = []
        for priority_level in ["high_priority", "medium_priority", "low_priority"]:
            for ann_type, ann_list in categorized_annotations.get(priority_level, {}).items():
                for annotation_text in ann_list:
                    priority_num = 1 if priority_level == "high_priority" else 2 if priority_level == "medium_priority" else 3
                    all_annotations.append((annotation_text, ann_type, priority_num))
        
        # Distribute annotations across pages
        annotations_per_page = max(1, len(all_annotations) // len(self.page_layouts))
        
        for page_num, layout in enumerate(self.page_layouts):
            # Get annotations for this page
            start_idx = page_num * annotations_per_page
            end_idx = start_idx + annotations_per_page
            if page_num == len(self.page_layouts) - 1:  # Last page gets remaining annotations
                end_idx = len(all_annotations)
            
            page_annotations = all_annotations[start_idx:end_idx]
            page_boxes = self._generate_page_annotations_distributed(page_num, layout, page_annotations)
            smart_boxes.extend(page_boxes)
        
        return smart_boxes
    
    def _generate_page_annotations(self, page_num: int, layout: Dict, annotations: Dict) -> List[SmartAnnotationBox]:
        """Generate annotations for a specific page with intelligent content linking."""
        boxes = []
        white_spaces = layout["white_spaces"]
        sections = layout["section_boundaries"]
        content_areas = layout["content_areas"]
        
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
                    
                    # Find relevant content area for this annotation
                    target_content = self._find_relevant_content_area(ann_type, sections, content_areas)
                    
                    # Find specific text to highlight
                    highlights = self._find_content_highlights(page_num, ann_type, annotation_text)
                    
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
                                2 if priority_level == "medium_priority" else 3,
                        related_highlights=highlights,
                        target_content_area=target_content
                    )
                    
                    boxes.append(box)
                    current_y += spacing
                    annotations_placed += 1
        
        return boxes
    
    def _generate_page_annotations_distributed(self, page_num: int, layout: Dict, page_annotations: List[Tuple[str, str, int]]) -> List[SmartAnnotationBox]:
        """Generate annotations for a specific page with distributed content."""
        boxes = []
        white_spaces = layout["white_spaces"]
        sections = layout["section_boundaries"]
        content_areas = layout["content_areas"]
        
        if not white_spaces or not page_annotations:
            return boxes
        
        # Use the best available white space (highest priority)
        primary_space = sorted(white_spaces, key=lambda x: x["priority"])[0]
        
        # Calculate available space for annotations
        available_width = primary_space["width"] - 10
        available_height = primary_space["height"] - 40
        start_y = primary_space["y"] + 20
        
        current_y = start_y
        
        # Place annotations for this page with dynamic sizing
        for i, (annotation_text, ann_type, priority) in enumerate(page_annotations):
            
            # Calculate optimal box size for this annotation
            remaining_height = available_height - (current_y - start_y)
            if remaining_height < 45:  # Not enough space for minimum box
                break
                
            box_width, box_height = self._calculate_optimal_box_size(
                annotation_text, priority, available_width, remaining_height
            )
            
            # Find relevant content area for this annotation
            target_content = self._find_relevant_content_area(ann_type, sections, content_areas)
            
            # Find specific text to highlight
            highlights = self._find_content_highlights(page_num, ann_type, annotation_text)
            
            # Create smart annotation box with page number
            box = SmartAnnotationBox(
                x=primary_space["x"] + 5,
                y=current_y,
                width=box_width,
                height=box_height,
                text=annotation_text,
                annotation_type=ann_type,
                content_relevance=self._find_content_relevance(ann_type, sections),
                color=self.annotation_colors.get(ann_type, (0.5, 0.5, 0.5)),
                priority=priority,
                related_highlights=highlights,
                target_content_area=target_content
            )
            
            # Store page number with the box
            box.page_num = page_num
            
            boxes.append(box)
            current_y += box_height + 15  # Increased spacing to prevent overlap
        
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
    
    def _find_relevant_content_area(self, annotation_type: str, sections: List[Dict], content_areas: List[Dict]) -> Tuple[float, float, float, float]:
        """Find the most relevant content area for this annotation type."""
        relevance_map = {
            "engagement": ["objectives", "activities"],
            "differentiation": ["activities", "materials"], 
            "assessment": ["assessment", "activities"],
            "improvement": ["activities", "objectives"],
            "strength": ["objectives", "activities"],
            "resource": ["materials", "activities"],
            "extension": ["activities"],
            "cultural": ["objectives", "activities"]
        }
        
        target_sections = relevance_map.get(annotation_type, ["activities"])
        
        # Find matching section
        for section in sections:
            if section["type"] in target_sections:
                bbox = section["bbox"]
                return (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
        
        # Fallback to largest content area
        if content_areas:
            largest = max(content_areas, key=lambda x: x["area"])
            bbox = largest["bbox"]
            return (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
        
        return None
    
    def _find_content_highlights(self, page_num: int, annotation_type: str, annotation_text: str) -> List[ContentHighlight]:
        """Find specific content to highlight for this annotation."""
        highlights = []
        
        if not self.doc or page_num >= len(self.doc):
            return highlights
        
        page = self.doc[page_num]
        text_blocks = page.get_text("dict")
        
        # Define keywords to highlight based on annotation type
        highlight_keywords = {
            "engagement": ["actividad", "juego", "participar", "interactivo", "estudiantes"],
            "differentiation": ["nivel", "diferentes", "apoyo", "adaptación", "individual"],
            "assessment": ["evaluación", "observar", "revisar", "compartir", "reflexionar"],
            "improvement": ["mejorar", "añadir", "incluir", "considerar", "desarrollar"],
            "strength": ["efectivo", "bueno", "excelente", "apropiado", "adecuado"],
            "resource": ["materiales", "recursos", "tarjetas", "libro", "apoyo"],
            "extension": ["extensión", "adicional", "más", "continuar", "ampliar"],
            "cultural": ["cultura", "español", "idioma", "lengua", "nativo"]
        }
        
        keywords = highlight_keywords.get(annotation_type, [])
        
        # Search for keywords in text blocks
        if "blocks" in text_blocks:
            for block in text_blocks["blocks"]:
                if "lines" in block and "bbox" in block:
                    block_text = ""
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                if "text" in span:
                                    block_text += span["text"].lower() + " "
                    
                    # Check if any keyword matches
                    for keyword in keywords:
                        if keyword in block_text:
                            bbox = block["bbox"]
                            highlights.append(ContentHighlight(
                                x=bbox[0],
                                y=bbox[1],
                                width=bbox[2] - bbox[0],
                                height=bbox[3] - bbox[1],
                                text_content=block_text[:100],
                                highlight_color=self.annotation_colors.get(annotation_type, (1.0, 1.0, 0.0)),
                                annotation_type=annotation_type
                            ))
                            break  # Only one highlight per block
        
        return highlights[:2]  # Limit to 2 highlights per annotation
    
    def _apply_smart_annotations(self, smart_boxes: List[SmartAnnotationBox]):
        """Apply smart annotation boxes to the PDF."""
        
        # Group boxes by page using stored page numbers
        page_boxes = {}
        for box in smart_boxes:
            page_num = getattr(box, 'page_num', 0)  # Use stored page number or default to 0
            if page_num not in page_boxes:
                page_boxes[page_num] = []
            page_boxes[page_num].append(box)
        
        # Apply annotations to each page
        for page_num, boxes in page_boxes.items():
            if page_num < len(self.doc):
                page = self.doc[page_num]
                
                for box in boxes:
                    # First, add content highlights
                    if box.related_highlights:
                        for highlight in box.related_highlights:
                            self._add_content_highlight(page, highlight)
                    
                    # Add visual connector if there's a target content area
                    if box.target_content_area:
                        self._add_visual_connector(page, box, box.target_content_area)
                    
                    # Finally, add the annotation box
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
        
        # Add white background for text with better contrast
        text_rect = fitz.Rect(box.x + 3, box.y + 3, box.x + box.width - 3, box.y + box.height - 3)
        page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
        
        # Add shadow effect for better readability
        shadow_rect = fitz.Rect(box.x + 5, box.y + 5, box.x + box.width - 1, box.y + box.height - 1)
        page.draw_rect(shadow_rect, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9), width=0)
        
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
        """Add intelligently formatted text to annotation box with dynamic sizing."""
        
        # Larger, more readable font sizes based on priority
        font_size = 10 if priority == 1 else 9 if priority == 2 else 8
        
        # Use the same text calculation method for consistency
        max_width = rect.width - 12  # Account for padding
        actual_width, actual_height, lines = self._calculate_text_dimensions(text, font_size, max_width)
        
        # Add lines with proper spacing
        line_height = font_size + 3
        y_offset = 8
        
        # Display all calculated lines (no arbitrary limit)
        for i, line in enumerate(lines):
            if y_offset + line_height > rect.height - 8:
                # If we run out of space, show "..." to indicate truncation
                if i > 0:  # Only show ellipsis if we've shown at least one line
                    truncated_line = lines[i-1][:-3] + "..." if len(lines[i-1]) > 3 else "..."
                    text_point = fitz.Point(rect.x0 + 6, rect.y0 + (y_offset - line_height) + line_height)
                    page.insert_text(
                        text_point,
                        truncated_line,
                        fontsize=font_size,
                        color=(0, 0, 0),
                        fontname="helv"
                    )
                break
            
            text_point = fitz.Point(rect.x0 + 6, rect.y0 + y_offset + line_height)
            
            # Bold for first line (icon + beginning), regular for others
            font_name = "hebo" if i == 0 else "helv"  # Bold for first line
            
            # High contrast black text on white background
            page.insert_text(
                text_point,
                line,
                fontsize=font_size,
                color=(0, 0, 0),  # Pure black for maximum contrast
                fontname=font_name
            )
            y_offset += line_height
    
    def _add_content_highlight(self, page, highlight: ContentHighlight):
        """Add highlighting to relevant content with proper transparency."""
        # Create highlight rectangle with transparency
        rect = fitz.Rect(highlight.x, highlight.y, highlight.x + highlight.width, highlight.y + highlight.height)
        
        # Use very light, transparent highlighting that doesn't block text
        base_color = highlight.highlight_color
        highlight_color = tuple(min(1.0, c + 0.6) for c in base_color)  # Much lighter
        
        # Add very subtle transparent highlight overlay with low opacity
        annot = page.add_highlight_annot(rect)
        annot.set_colors({"stroke": highlight_color})  # Highlights don't need fill color
        annot.set_opacity(0.2)  # Very low opacity to preserve text readability
        annot.update()
        
        # Add subtle border only (no fill)
        page.draw_rect(rect, color=base_color, fill=None, width=0.5)
    
    def _add_visual_connector(self, page, annotation_box: SmartAnnotationBox, target_area: Tuple[float, float, float, float]):
        """Add visual connector line between annotation and relevant content."""
        if not target_area:
            return
        
        # Calculate connection points
        # From annotation box (left edge, middle)
        from_x = annotation_box.x
        from_y = annotation_box.y + annotation_box.height / 2
        
        # To target content area (closest edge)
        target_x, target_y, target_w, target_h = target_area
        to_x = target_x + target_w  # Right edge of content
        to_y = target_y + target_h / 2  # Middle height
        
        # Adjust if annotation is to the left of content
        if from_x < target_x:
            to_x = target_x  # Left edge instead
        
        # Draw curved connection line
        self._draw_curved_connector(page, from_x, from_y, to_x, to_y, annotation_box.color)
    
    def _draw_curved_connector(self, page, x1: float, y1: float, x2: float, y2: float, color: Tuple[float, float, float]):
        """Draw a curved connector line."""
        # Create a curved path using control points
        mid_x = (x1 + x2) / 2
        
        # Control points for bezier curve
        ctrl1_x = x1 + (mid_x - x1) * 0.7
        ctrl1_y = y1
        ctrl2_x = x2 - (x2 - mid_x) * 0.7
        ctrl2_y = y2
        
        # Draw the curved line using multiple segments
        num_segments = 10
        for i in range(num_segments):
            t = i / num_segments
            t_next = (i + 1) / num_segments
            
            # Bezier curve calculation
            start_x = self._bezier_point(t, x1, ctrl1_x, ctrl2_x, x2)
            start_y = self._bezier_point(t, y1, ctrl1_y, ctrl2_y, y2)
            end_x = self._bezier_point(t_next, x1, ctrl1_x, ctrl2_x, x2)
            end_y = self._bezier_point(t_next, y1, ctrl1_y, ctrl2_y, y2)
            
            # Draw line segment
            page.draw_line(fitz.Point(start_x, start_y), fitz.Point(end_x, end_y), 
                          color=color, width=1.5)
        
        # Add small arrow at the end
        arrow_size = 3
        page.draw_line(fitz.Point(x2, y2), 
                      fitz.Point(x2 - arrow_size, y2 - arrow_size), 
                      color=color, width=1.5)
        page.draw_line(fitz.Point(x2, y2), 
                      fitz.Point(x2 - arrow_size, y2 + arrow_size), 
                      color=color, width=1.5)
    
    def _bezier_point(self, t: float, p0: float, p1: float, p2: float, p3: float) -> float:
        """Calculate point on cubic bezier curve."""
        return (1-t)**3 * p0 + 3*(1-t)**2*t * p1 + 3*(1-t)*t**2 * p2 + t**3 * p3
    
    def _calculate_text_dimensions(self, text: str, font_size: int, max_width: float) -> Tuple[float, float, List[str]]:
        """Calculate required dimensions for text with word wrapping."""
        
        # Estimate character width (varies by font, this is approximate)
        char_width = font_size * 0.5  # Rough estimate for helvetica
        max_chars_per_line = int(max_width / char_width)
        
        # Word wrap the text
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_chars_per_line or not current_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Calculate dimensions
        line_height = font_size + 3
        total_height = len(lines) * line_height + 16  # 16 for padding
        
        # Calculate actual width needed (longest line)
        max_line_length = max(len(line) for line in lines) if lines else 0
        actual_width = min(max_width, max_line_length * char_width + 12)  # 12 for padding
        
        return actual_width, total_height, lines
    
    def _calculate_optimal_box_size(self, text: str, priority: int, available_width: float, available_height: float) -> Tuple[float, float]:
        """Calculate optimal box size for given text content."""
        
        # Font size based on priority
        font_size = 10 if priority == 1 else 9 if priority == 2 else 8
        
        # Start with minimum constraints
        min_width = 150  # Increased minimum width for better readability
        min_height = 50  # Slightly increased minimum height
        max_width = min(available_width - 20, 300)  # Allow even wider boxes for longer text
        max_height = min(available_height * 0.9, 400)  # Increased max height for expandable boxes
        
        # Calculate text requirements
        actual_width, actual_height, lines = self._calculate_text_dimensions(text, font_size, max_width)
        
        # Ensure minimums but respect text requirements
        final_width = max(min_width, min(actual_width, max_width))
        final_height = max(min_height, min(actual_height, max_height))
        
        return final_width, final_height


def create_smart_overlay_pdf_from_json(json_file: str, original_pdf: str = None, theme: str = None) -> str:
    """Create smart overlay PDF from saved JSON results."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            annotations_data = json.load(f)
        
        if original_pdf is None:
            original_pdf = annotations_data.get('lesson_info', {}).get('pdf_path', 'fonetica8.pdf')
        
        generator = SmartOverlayAnnotator(original_pdf, theme=theme)
        output_file = generator.create_smart_overlay_pdf(annotations_data)
        
        return output_file
        
    except Exception as e:
        print(f"Error creating smart overlay PDF from JSON: {e}")
        return None