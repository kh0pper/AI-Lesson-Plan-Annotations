import io
from datetime import datetime
from typing import Dict, List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import blue, red, green, black, gray
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
import PyPDF2
import json


class PDFAnnotationGenerator:
    """Generate annotated PDF with AI insights overlaid on original lesson plan."""
    
    def __init__(self, original_pdf_path: str):
        self.original_pdf_path = original_pdf_path
        self.annotations = {}
        self.output_path = ""
        
    def create_annotated_pdf(self, annotations_data: Dict, output_filename: str = None) -> str:
        """Create a new PDF with annotations overlaid on the original."""
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"annotated_lesson_plan_{timestamp}.pdf"
        
        self.output_path = output_filename
        self.annotations = annotations_data
        
        # Create the annotation document
        annotation_buffer = io.BytesIO()
        self._create_annotation_document(annotation_buffer)
        
        # Combine with original PDF
        self._combine_pdfs(annotation_buffer, output_filename)
        
        return output_filename
    
    def _create_annotation_document(self, buffer):
        """Create a comprehensive annotation document."""
        doc = SimpleDocTemplate(
            buffer,
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
            fontSize=16,
            spaceAfter=30,
            textColor=blue,
            alignment=TA_LEFT
        )
        
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=red,
            alignment=TA_LEFT
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leftIndent=0.2*inch
        )
        
        # Build the story
        story = []
        
        # Title page
        story.append(Paragraph("🎓 AI LESSON PLAN ANNOTATIONS", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Lesson info
        if 'lesson_info' in self.annotations:
            info = self.annotations['lesson_info']
            story.append(Paragraph("📋 LESSON INFORMATION", section_style))
            
            lesson_details = f"""
            <b>PDF File:</b> {info.get('pdf_path', 'N/A')}<br/>
            <b>Analysis Date:</b> {info.get('timestamp', 'N/A')}<br/>
            <b>Parameter Preset:</b> {info.get('parameter_preset', 'N/A')}<br/>
            <b>Grade Level:</b> {info.get('structure', {}).get('grade_level', 'N/A')}<br/>
            <b>Week/Day:</b> {info.get('structure', {}).get('week', 'N/A')}
            """
            story.append(Paragraph(lesson_details, body_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Main annotations
        if 'annotations' in self.annotations:
            story.append(Paragraph("🤖 AI ANALYSIS & RECOMMENDATIONS", title_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Parse and format the annotations
            annotation_text = self.annotations['annotations']
            sections = self._parse_annotation_sections(annotation_text)
            
            for section_title, content in sections.items():
                story.append(Paragraph(section_title, section_style))
                
                # Process content to handle lists and formatting
                formatted_content = self._format_content(content)
                story.append(Paragraph(formatted_content, body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Usage statistics
        if 'usage' in self.annotations:
            story.append(PageBreak())
            story.append(Paragraph("📊 ANALYSIS STATISTICS", section_style))
            usage = self.annotations['usage']
            usage_text = f"""
            <b>Prompt Tokens:</b> {usage.get('prompt_tokens', 'N/A')}<br/>
            <b>Completion Tokens:</b> {usage.get('completion_tokens', 'N/A')}<br/>
            <b>Total Tokens:</b> {usage.get('total_tokens', 'N/A')}
            """
            story.append(Paragraph(usage_text, body_style))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
    
    def _parse_annotation_sections(self, text: str) -> Dict[str, str]:
        """Parse annotation text into sections."""
        sections = {}
        current_section = ""
        current_content = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('###') or line.startswith('##'):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.replace('#', '').strip()
                current_content = []
            elif line and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _format_content(self, content: str) -> str:
        """Format content for better display in PDF."""
        # Handle bullet points and formatting
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Convert markdown-style formatting
            if line.startswith('**') and line.endswith('**'):
                line = f"<b>{line[2:-2]}</b>"
            elif '**' in line:
                line = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
            
            # Handle numbered lists
            if line[0].isdigit() and line[1:3] == '. ':
                line = f"<b>{line}</b>"
            
            # Handle bullet points
            if line.startswith('- ') or line.startswith('• '):
                line = f"• {line[2:]}"
            
            formatted_lines.append(line)
        
        return '<br/>'.join(formatted_lines)
    
    def _combine_pdfs(self, annotation_buffer, output_filename: str):
        """Combine the original PDF with annotations."""
        try:
            # Read the original PDF
            with open(self.original_pdf_path, 'rb') as original_file:
                original_reader = PyPDF2.PdfReader(original_file)
                annotation_reader = PyPDF2.PdfReader(annotation_buffer)
                
                writer = PyPDF2.PdfWriter()
                
                # Add original pages first
                for page in original_reader.pages:
                    writer.add_page(page)
                
                # Add annotation pages
                for page in annotation_reader.pages:
                    writer.add_page(page)
                
                # Write the combined PDF
                with open(output_filename, 'wb') as output_file:
                    writer.write(output_file)
                    
        except Exception as e:
            # If combining fails, just save the annotation document
            print(f"Warning: Could not combine PDFs ({e}). Saving annotations only.")
            annotation_buffer.seek(0)
            with open(output_filename, 'wb') as output_file:
                output_file.write(annotation_buffer.read())
    
    def create_side_by_side_pdf(self, annotations_data: Dict, output_filename: str = None) -> str:
        """Create a side-by-side view with original and annotations."""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"side_by_side_annotations_{timestamp}.pdf"
        
        # For now, create the appended version
        # Side-by-side would require more complex layout management
        return self.create_annotated_pdf(annotations_data, output_filename)


def create_annotated_pdf_from_json(json_file: str, original_pdf: str = None) -> str:
    """Create annotated PDF from saved JSON results."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            annotations_data = json.load(f)
        
        if original_pdf is None:
            original_pdf = annotations_data.get('lesson_info', {}).get('pdf_path', 'fonetica8.pdf')
        
        generator = PDFAnnotationGenerator(original_pdf)
        output_file = generator.create_annotated_pdf(annotations_data)
        
        return output_file
        
    except Exception as e:
        print(f"Error creating annotated PDF from JSON: {e}")
        return None