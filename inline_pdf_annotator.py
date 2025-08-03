import io
import re
from datetime import datetime
from typing import Dict, List, Tuple
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import blue, red, green, black, gray, orange, purple
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
import PyPDF2
import json


class InlinePDFAnnotator:
    """Enhanced PDF annotator that adds inline annotations alongside lesson plan content."""
    
    def __init__(self, original_pdf_path: str):
        self.original_pdf_path = original_pdf_path
        self.annotations = {}
        self.lesson_sections = []
        self.output_path = ""
        
    def create_inline_annotated_pdf(self, annotations_data: Dict, output_filename: str = None) -> str:
        """Create PDF with inline annotations integrated into the lesson plan."""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"inline_annotated_lesson_{timestamp}.pdf"
        
        self.output_path = output_filename
        self.annotations = annotations_data
        
        # Extract and analyze lesson content
        lesson_content = self._extract_lesson_content()
        
        # Parse AI annotations into actionable insights
        parsed_annotations = self._parse_ai_annotations()
        
        # Create sections with inline annotations
        annotated_sections = self._create_annotated_sections(lesson_content, parsed_annotations)
        
        # Generate the annotated PDF
        self._generate_inline_pdf(annotated_sections, output_filename)
        
        return output_filename
    
    def _extract_lesson_content(self) -> Dict:
        """Extract and structure lesson plan content."""
        try:
            with open(self.original_pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page in pdf_reader.pages:
                    full_text += page.extract_text() + "\n"
                
                # Structure the content into logical sections
                sections = self._identify_lesson_sections(full_text)
                return sections
                
        except Exception as e:
            print(f"Error extracting lesson content: {e}")
            return {"full_text": "", "sections": []}
    
    def _identify_lesson_sections(self, text: str) -> Dict:
        """Identify different sections of the lesson plan."""
        sections = {
            "header": "",
            "objectives": "",
            "materials": "",
            "activities": [],
            "assessment": "",
            "full_text": text
        }
        
        lines = text.split('\n')
        current_section = "header"
        current_activity = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify section headers
            if any(keyword in line.lower() for keyword in ['objetivos', 'objectives']):
                current_section = "objectives"
                continue
            elif any(keyword in line.lower() for keyword in ['materiales', 'materials']):
                current_section = "materials"
                continue
            elif any(keyword in line.lower() for keyword in ['nosotros leemos', 'lectura compartida', 'actividad']):
                if current_activity:
                    sections["activities"].append(current_activity)
                current_activity = line + "\n"
                current_section = "activity"
                continue
            elif any(keyword in line.lower() for keyword in ['evaluación', 'assessment', 'compartir']):
                if current_activity:
                    sections["activities"].append(current_activity)
                    current_activity = ""
                current_section = "assessment"
                continue
            
            # Add content to appropriate section
            if current_section == "header" and len(sections["header"]) < 500:
                sections["header"] += line + "\n"
            elif current_section == "objectives":
                sections["objectives"] += line + "\n"
            elif current_section == "materials":
                sections["materials"] += line + "\n"
            elif current_section == "activity":
                current_activity += line + "\n"
            elif current_section == "assessment":
                sections["assessment"] += line + "\n"
        
        # Add final activity if exists
        if current_activity:
            sections["activities"].append(current_activity)
        
        return sections
    
    def _parse_ai_annotations(self) -> Dict:
        """Parse AI annotations into section-specific insights."""
        if 'annotations' not in self.annotations:
            return {}
        
        annotation_text = self.annotations['annotations']
        
        # Extract different types of annotations
        parsed = {
            "pedagogical_strengths": self._extract_annotation_section(annotation_text, "Pedagogical Strengths"),
            "engagement_opportunities": self._extract_annotation_section(annotation_text, "Student Engagement"),
            "assessment_suggestions": self._extract_annotation_section(annotation_text, "Assessment Suggestions"),
            "differentiation": self._extract_annotation_section(annotation_text, "Differentiation Strategies"),
            "resource_optimization": self._extract_annotation_section(annotation_text, "Resource Optimization"),
            "extension_activities": self._extract_annotation_section(annotation_text, "Extension Activities"),
            "improvements": self._extract_annotation_section(annotation_text, "Areas for Improvement"),
            "cultural_considerations": self._extract_annotation_section(annotation_text, "Cultural/Linguistic")
        }
        
        return parsed
    
    def _extract_annotation_section(self, text: str, section_name: str) -> List[str]:
        """Extract specific annotation section as bullet points."""
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            line = line.strip()
            
            if section_name.lower() in line.lower() and ('**' in line or '##' in line):
                in_section = True
                continue
            elif in_section and ('**' in line or '##' in line) and section_name.lower() not in line.lower():
                break
            elif in_section and line:
                # Clean up bullet points and formatting
                clean_line = line.replace('*', '').replace('#', '').strip()
                if clean_line and not clean_line.startswith('###'):
                    section_content.append(clean_line)
        
        return section_content[:3]  # Limit to top 3 points per section
    
    def _create_annotated_sections(self, lesson_content: Dict, annotations: Dict) -> List[Dict]:
        """Create lesson sections with inline annotations."""
        annotated_sections = []
        
        # Title section with overview
        annotated_sections.append({
            "type": "title",
            "content": lesson_content.get("header", "Lesson Plan"),
            "annotations": {
                "type": "overview",
                "insights": annotations.get("pedagogical_strengths", [])[:2]
            }
        })
        
        # Objectives with engagement suggestions
        if lesson_content.get("objectives"):
            annotated_sections.append({
                "type": "section",
                "title": "📋 Objetivos del Estudiante",
                "content": lesson_content["objectives"],
                "annotations": {
                    "type": "engagement",
                    "title": "💡 Engagement Opportunities",
                    "insights": annotations.get("engagement_opportunities", [])[:2]
                }
            })
        
        # Materials with resource optimization
        if lesson_content.get("materials"):
            annotated_sections.append({
                "type": "section", 
                "title": "📦 Materiales",
                "content": lesson_content["materials"],
                "annotations": {
                    "type": "optimization",
                    "title": "🔧 Resource Optimization",
                    "insights": annotations.get("resource_optimization", [])[:2]
                }
            })
        
        # Activities with differentiation and extensions
        for i, activity in enumerate(lesson_content.get("activities", [])):
            annotation_type = ["differentiation", "extension_activities", "improvements"][i % 3]
            annotation_titles = ["🎯 Differentiation Ideas", "➕ Extension Activities", "🔧 Improvement Suggestions"]
            
            annotated_sections.append({
                "type": "activity",
                "title": f"🎓 Actividad {i+1}",
                "content": activity,
                "annotations": {
                    "type": annotation_type,
                    "title": annotation_titles[i % 3],
                    "insights": annotations.get(annotation_type, [])[:2]
                }
            })
        
        # Assessment with suggestions
        if lesson_content.get("assessment"):
            annotated_sections.append({
                "type": "section",
                "title": "📊 Evaluación",
                "content": lesson_content["assessment"],
                "annotations": {
                    "type": "assessment",
                    "title": "📈 Assessment Enhancement",
                    "insights": annotations.get("assessment_suggestions", [])[:2]
                }
            })
        
        return annotated_sections
    
    def _generate_inline_pdf(self, sections: List[Dict], output_filename: str):
        """Generate PDF with inline annotations."""
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=blue,
            alignment=TA_CENTER
        )
        
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=purple,
            alignment=TA_LEFT
        )
        
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leftIndent=0.2*inch
        )
        
        annotation_style = ParagraphStyle(
            'Annotation',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=5,
            alignment=TA_LEFT,
            leftIndent=0.3*inch,
            textColor=blue,
            backColor=None
        )
        
        annotation_title_style = ParagraphStyle(
            'AnnotationTitle',
            parent=styles['Heading3'],
            fontSize=11,
            spaceBefore=8,
            spaceAfter=5,
            textColor=orange,
            alignment=TA_LEFT,
            leftIndent=0.2*inch
        )
        
        # Build story
        story = []
        
        # Add main title
        story.append(Paragraph("🎓 AI-Enhanced Lesson Plan", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Process each section
        for section in sections:
            if section["type"] == "title":
                # Lesson title and overview
                story.append(Paragraph(section["content"][:200] + "...", content_style))
                
                if section["annotations"]["insights"]:
                    story.append(Paragraph("🌟 Key Strengths Identified", annotation_title_style))
                    for insight in section["annotations"]["insights"]:
                        story.append(Paragraph(f"• {insight}", annotation_style))
                story.append(Spacer(1, 0.2*inch))
                
            else:
                # Section content
                story.append(Paragraph(section["title"], section_title_style))
                
                # Create two-column layout: content + annotations
                content_text = section["content"][:400] + ("..." if len(section["content"]) > 400 else "")
                
                # Main content
                story.append(Paragraph(content_text, content_style))
                
                # Inline annotations
                if section["annotations"]["insights"]:
                    story.append(Paragraph(section["annotations"]["title"], annotation_title_style))
                    for insight in section["annotations"]["insights"]:
                        story.append(Paragraph(f"• {insight[:150]}{'...' if len(insight) > 150 else ''}", annotation_style))
                
                story.append(Spacer(1, 0.15*inch))
        
        # Add summary section
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("📋 Summary of AI Recommendations", section_title_style))
        
        # Get cultural considerations if available
        cultural_insights = self._parse_ai_annotations().get("cultural_considerations", [])
        if cultural_insights:
            story.append(Paragraph("🌍 Cultural & Linguistic Considerations", annotation_title_style))
            for insight in cultural_insights[:2]:
                story.append(Paragraph(f"• {insight}", annotation_style))
        
        # Build PDF
        doc.build(story)


def create_inline_annotated_pdf_from_json(json_file: str, original_pdf: str = None) -> str:
    """Create inline annotated PDF from saved JSON results."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            annotations_data = json.load(f)
        
        if original_pdf is None:
            original_pdf = annotations_data.get('lesson_info', {}).get('pdf_path', 'fonetica8.pdf')
        
        generator = InlinePDFAnnotator(original_pdf)
        output_file = generator.create_inline_annotated_pdf(annotations_data)
        
        return output_file
        
    except Exception as e:
        print(f"Error creating inline annotated PDF from JSON: {e}")
        return None