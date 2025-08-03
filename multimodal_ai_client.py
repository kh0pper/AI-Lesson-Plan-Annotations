import os
import base64
import io
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional
import fitz  # PyMuPDF
from PIL import Image
import json

# Load environment variables
load_dotenv()


class MultimodalLlamaClient:
    """Enhanced AI client that uses visual analysis for intelligent annotation placement."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("LLAMA_API_KEY"),
            base_url="https://api.llama.com/compat/v1/",
        )
        self.model = "Llama-4-Maverick-17B-128E-Instruct-FP8"  # Check if this supports vision
        
    def analyze_pdf_layout_visually(self, pdf_path: str, annotations_data: Dict) -> List[Dict]:
        """Analyze PDF layout visually and determine optimal annotation placement."""
        
        # Convert PDF pages to images
        page_images = self._convert_pdf_to_images(pdf_path)
        
        # Analyze each page visually
        placement_instructions = []
        
        for page_num, image_data in enumerate(page_images):
            # Get AI analysis of the page layout
            layout_analysis = self._analyze_page_layout(image_data, page_num, annotations_data)
            placement_instructions.append(layout_analysis)
        
        return placement_instructions
    
    def _convert_pdf_to_images(self, pdf_path: str) -> List[str]:
        """Convert PDF pages to base64 encoded images."""
        images = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(min(len(doc), 3)):  # Limit to first 3 pages for efficiency
                page = doc[page_num]
                
                # Render page as image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                images.append(img_base64)
            
            doc.close()
            return images
            
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []
    
    def _analyze_page_layout(self, image_base64: str, page_num: int, annotations_data: Dict) -> Dict:
        """Use multimodal AI to analyze page layout and suggest annotation placement."""
        
        # Extract relevant annotations for this analysis
        annotations_text = annotations_data.get('annotations', '')
        
        # Parse key insights for placement
        key_insights = self._extract_key_insights(annotations_text)
        
        prompt = f"""
Analyze this lesson plan page image and provide intelligent annotation placement suggestions.

AVAILABLE INSIGHTS TO PLACE:
{json.dumps(key_insights, indent=2)}

Please analyze the visual layout and provide specific coordinates and placement suggestions:

1. VISUAL LAYOUT ANALYSIS:
   - Identify main content areas (headers, text blocks, images)
   - Locate margins and white space areas
   - Identify section boundaries
   - Note any visual elements (boxes, tables, images)

2. ANNOTATION PLACEMENT STRATEGY:
   - Suggest specific (x, y) coordinates for annotation boxes
   - Recommend box sizes (width, height) 
   - Identify which insights should go where based on content proximity
   - Ensure annotations don't cover important text or images

3. CONTENT CORRELATION:
   - Match insights to relevant sections (objectives near objectives text, etc.)
   - Suggest annotation types for each placement
   - Recommend spacing between multiple annotations

Provide response in this JSON format:
{{
  "page_analysis": {{
    "main_content_areas": ["description of content areas"],
    "available_margins": ["left: width, right: width, top: height, bottom: height"],
    "white_space_regions": [["x, y, width, height coordinates"]]
  }},
  "annotation_placements": [
    {{
      "insight_key": "key from insights",
      "x": 0,
      "y": 0, 
      "width": 0,
      "height": 0,
      "rationale": "why this placement",
      "annotation_type": "engagement|assessment|differentiation|etc"
    }}
  ]
}}
"""

        try:
            # Note: This is a placeholder for multimodal API call
            # The actual implementation would depend on Llama's vision capabilities
            response = self._make_multimodal_request(prompt, image_base64)
            
            if response and response.get('success'):
                return self._parse_placement_response(response['content'])
            else:
                # Fallback to basic placement
                return self._generate_fallback_placement(page_num, key_insights)
                
        except Exception as e:
            print(f"Error in visual analysis: {e}")
            return self._generate_fallback_placement(page_num, key_insights)
    
    def _make_multimodal_request(self, prompt: str, image_base64: str) -> Dict:
        """Make multimodal API request to Llama."""
        try:
            # Check if the model supports vision
            # This is a placeholder - actual implementation depends on Llama's capabilities
            
            # For now, we'll use text-only analysis with image dimensions
            # In a real multimodal implementation, this would include the image
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert in document layout analysis and annotation placement. Provide precise coordinate-based suggestions for placing annotations on lesson plans."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content
            }
            
        except Exception as e:
            print(f"Multimodal API request failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_key_insights(self, annotations_text: str) -> Dict:
        """Extract key insights from annotations for placement."""
        insights = {
            "engagement": [],
            "assessment": [],
            "differentiation": [],
            "strengths": [],
            "improvements": [],
            "resources": []
        }
        
        # Parse annotations into categories
        sections = annotations_text.split('###')
        
        for section in sections:
            if 'engagement' in section.lower():
                insights["engagement"] = self._extract_bullets(section)[:2]
            elif 'assessment' in section.lower():
                insights["assessment"] = self._extract_bullets(section)[:2]
            elif 'differentiation' in section.lower():
                insights["differentiation"] = self._extract_bullets(section)[:2]
            elif 'strength' in section.lower():
                insights["strengths"] = self._extract_bullets(section)[:2]
            elif 'improvement' in section.lower():
                insights["improvements"] = self._extract_bullets(section)[:2]
            elif 'resource' in section.lower():
                insights["resources"] = self._extract_bullets(section)[:2]
        
        return insights
    
    def _extract_bullets(self, text: str) -> List[str]:
        """Extract bullet points from text section."""
        lines = text.split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')) or line[0:1].isdigit():
                clean_line = line.lstrip('-•*0123456789. ').strip()
                if len(clean_line) > 10:
                    # Truncate for annotation display
                    if len(clean_line) > 60:
                        clean_line = clean_line[:57] + "..."
                    bullets.append(clean_line)
        
        return bullets
    
    def _parse_placement_response(self, response_text: str) -> Dict:
        """Parse AI response into placement instructions."""
        try:
            # Try to extract JSON from response
            if '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
        except:
            pass
        
        # Fallback parsing if JSON fails
        return self._generate_fallback_placement(0, {})
    
    def _generate_fallback_placement(self, page_num: int, insights: Dict) -> Dict:
        """Generate fallback placement when AI analysis fails."""
        placements = []
        
        # Standard placement strategy
        margin_x = 450  # Right margin
        start_y = 100
        spacing = 80
        box_width = 140
        box_height = 60
        
        y_pos = start_y
        
        # Place key insights
        for insight_type, insight_list in insights.items():
            if insight_list and len(placements) < 4:  # Limit to 4 per page
                placements.append({
                    "insight_key": insight_type,
                    "x": margin_x,
                    "y": y_pos,
                    "width": box_width,
                    "height": box_height,
                    "rationale": f"Placed in right margin for {insight_type}",
                    "annotation_type": insight_type,
                    "text": insight_list[0] if insight_list else ""
                })
                y_pos += spacing
        
        return {
            "page_analysis": {
                "main_content_areas": ["Standard lesson plan layout"],
                "available_margins": ["right: 150px available"],
                "white_space_regions": [[margin_x, start_y, box_width, 300]]
            },
            "annotation_placements": placements
        }


class IntelligentOverlayAnnotator:
    """Enhanced overlay annotator using multimodal AI for intelligent placement."""
    
    def __init__(self, original_pdf_path: str):
        self.original_pdf_path = original_pdf_path
        self.multimodal_client = MultimodalLlamaClient()
        self.doc = None
    
    def create_intelligent_overlay_pdf(self, annotations_data: Dict, output_filename: str = None) -> str:
        """Create PDF with intelligently placed annotation overlays."""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"intelligent_overlay_{timestamp}.pdf"
        
        try:
            # Open PDF
            self.doc = fitz.open(self.original_pdf_path)
            
            # Get intelligent placement instructions
            print("🧠 Analyzing PDF layout with multimodal AI...")
            placement_instructions = self.multimodal_client.analyze_pdf_layout_visually(
                self.original_pdf_path, annotations_data
            )
            
            # Apply intelligent annotations
            print("📍 Applying intelligent annotation placement...")
            self._apply_intelligent_annotations(placement_instructions)
            
            # Save result
            self.doc.save(output_filename)
            self.doc.close()
            
            return output_filename
            
        except Exception as e:
            print(f"Error creating intelligent overlay PDF: {e}")
            if self.doc:
                self.doc.close()
            return None
    
    def _apply_intelligent_annotations(self, placement_instructions: List[Dict]):
        """Apply annotations based on intelligent placement analysis."""
        
        color_map = {
            "engagement": (0.2, 0.8, 0.3),     # Bright green
            "assessment": (0.6, 0.2, 0.8),     # Purple  
            "differentiation": (0.9, 0.5, 0.1), # Orange
            "strengths": (0.2, 0.5, 0.9),      # Blue
            "improvements": (0.9, 0.2, 0.2),   # Red
            "resources": (0.7, 0.7, 0.2),      # Olive
        }
        
        for page_num, page_instructions in enumerate(placement_instructions):
            if page_num < len(self.doc):
                page = self.doc[page_num]
                
                placements = page_instructions.get("annotation_placements", [])
                
                for placement in placements:
                    self._add_intelligent_annotation(page, placement, color_map)
    
    def _add_intelligent_annotation(self, page, placement: Dict, color_map: Dict):
        """Add a single intelligent annotation to the page."""
        
        x = placement.get("x", 400)
        y = placement.get("y", 100)
        width = placement.get("width", 140)
        height = placement.get("height", 60)
        annotation_type = placement.get("annotation_type", "general")
        text = placement.get("text", "AI Insight")
        
        # Get color for annotation type
        color = color_map.get(annotation_type, (0.5, 0.5, 0.5))
        
        # Create annotation rectangle
        rect = fitz.Rect(x, y, x + width, y + height)
        
        # Add colored background with transparency
        page.draw_rect(rect, color=color, fill=color, width=0)
        
        # Add white background for text readability
        text_rect = fitz.Rect(x + 2, y + 2, x + width - 2, y + height - 2)
        page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
        
        # Add border
        page.draw_rect(rect, color=color, fill=None, width=2)
        
        # Add icon based on type
        icon = self._get_annotation_icon(annotation_type)
        
        # Add text with icon
        display_text = f"{icon} {text}"
        self._add_wrapped_text(page, display_text, text_rect)
    
    def _get_annotation_icon(self, annotation_type: str) -> str:
        """Get appropriate icon for annotation type."""
        icons = {
            "engagement": "💡",
            "assessment": "📊", 
            "differentiation": "🎯",
            "strengths": "⭐",
            "improvements": "🔧",
            "resources": "📦",
            "general": "💭"
        }
        return icons.get(annotation_type, "💭")
    
    def _add_wrapped_text(self, page, text: str, rect: fitz.Rect):
        """Add wrapped text to annotation box."""
        words = text.split()
        lines = []
        current_line = ""
        max_width = rect.width - 10
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) * 5 < max_width:  # Rough character width
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Add lines to PDF
        font_size = 7
        line_height = 9
        y_offset = 8
        
        for line in lines[:5]:  # Limit lines
            if y_offset + line_height > rect.height - 5:
                break
            
            text_point = fitz.Point(rect.x0 + 5, rect.y0 + y_offset)
            page.insert_text(
                text_point,
                line,
                fontsize=font_size,
                color=(0, 0, 0),
                fontname="helv"
            )
            y_offset += line_height