#!/usr/bin/env python3
"""
Combined PDF Annotator that merges Smart Overlay, Inline, and Traditional formats
into a single comprehensive PDF with color-coded sections.
"""

import os
import io
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import blue, black, red, green, orange, purple, brown, pink
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PyPDF2 import PdfWriter, PdfReader

from smart_overlay_annotator import SmartOverlayAnnotator
from inline_pdf_annotator import InlinePDFAnnotator
from pdf_annotator import PDFAnnotationGenerator


class CombinedPDFAnnotator:
    """Generate a single PDF combining all annotation formats with color-coded sections."""
    
    def __init__(self, original_pdf_path: str, theme: str = 'educational'):
        self.original_pdf_path = original_pdf_path
        self.theme = theme
        self.section_colors = self._load_section_colors(theme)
        
    def _load_section_colors(self, theme: str) -> Dict[str, Tuple[float, float, float]]:
        """Load section colors from themes.json."""
        try:
            themes_path = os.path.join(os.path.dirname(__file__), 'themes.json')
            with open(themes_path, 'r') as f:
                themes_data = json.load(f)
            
            if theme is None:
                theme = themes_data.get('default_theme', 'educational')
            
            if theme not in themes_data['themes']:
                theme = 'educational'
            
            colors = themes_data['themes'][theme]['colors']
            return {k: tuple(v) for k, v in colors.items()}
            
        except Exception as e:
            print(f"⚠️ Error loading theme colors: {e}, using defaults")
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
    
    def _map_section_to_color_category(self, section_title: str) -> str:
        """Map annotation section titles to color categories."""
        section_lower = section_title.lower()
        
        # Custom category mappings (for user-defined themes) - check first
        if 'must-do' in section_lower or 'must do' in section_lower:
            return 'category1'
        elif 'skip' in section_lower or 'omit' in section_lower or 'can be skipped' in section_lower:
            return 'category2'
        
        # For custom theme, use numbered categories
        if self.theme == 'custom':
            if any(term in section_lower for term in ['engagement', 'participation', 'student']):
                return 'category3'  # Student Engagement in custom theme
            elif any(term in section_lower for term in ['strategy', 'teaching', 'method']):
                return 'category4'  # Teaching Strategies
            elif any(term in section_lower for term in ['assessment', 'evaluation']):
                return 'category5'  # Assessment Methods
            elif any(term in section_lower for term in ['resource', 'material']):
                return 'category6'  # Resources & Materials
            elif any(term in section_lower for term in ['extension', 'enrich']):
                return 'category7'  # Extensions & Enrichment
            elif any(term in section_lower for term in ['cultural', 'linguistic']):
                return 'category8'  # Cultural Considerations
            else:
                return 'category1'  # Default for custom theme
        
        # Standard theme mappings (English)
        if any(term in section_lower for term in ['engagement', 'participation', 'student']):
            return 'engagement'
        elif any(term in section_lower for term in ['differentiation', 'differentiated', 'accommodate']):
            return 'differentiation'
        elif any(term in section_lower for term in ['assessment', 'evaluation', 'evaluate']):
            return 'assessment'
        elif any(term in section_lower for term in ['improvement', 'areas for improvement', 'enhance']):
            return 'improvement'
        elif any(term in section_lower for term in ['strength', 'pedagogical strengths', 'effective']):
            return 'strength'
        elif any(term in section_lower for term in ['resource', 'materials', 'optimization']):
            return 'resource'
        elif any(term in section_lower for term in ['extension', 'activities', 'deepen']):
            return 'extension'
        elif any(term in section_lower for term in ['cultural', 'linguistic', 'language']):
            return 'cultural'
        
        # Spanish mappings
        elif any(term in section_lower for term in ['participación', 'estudiantes', 'oportunidades']):
            return 'engagement'
        elif any(term in section_lower for term in ['diferenciación', 'estrategias']):
            return 'differentiation'
        elif any(term in section_lower for term in ['evaluación', 'sugerencias']):
            return 'assessment'
        elif any(term in section_lower for term in ['mejora', 'áreas']):
            return 'improvement'
        elif any(term in section_lower for term in ['fortalezas', 'pedagógicas']):
            return 'strength'
        elif any(term in section_lower for term in ['recursos', 'optimización', 'materiales']):
            return 'resource'
        elif any(term in section_lower for term in ['extensión', 'actividades']):
            return 'extension'
        elif any(term in section_lower for term in ['culturales', 'lingüísticas', 'consideraciones']):
            return 'cultural'
        
        # Default fallback
        return 'strength'
    
    def _rgb_to_reportlab_color(self, rgb_tuple: Tuple[float, float, float]):
        """Convert RGB tuple (0-1 range) to ReportLab color."""
        from reportlab.lib.colors import Color
        return Color(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
    
    def create_combined_pdf(self, annotations_data: Dict, output_filename: str = None) -> str:
        """Create a single PDF combining all three annotation formats."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_filename is None:
            output_filename = f"combined_annotations_{timestamp}.pdf"
        
        try:
            # Create temporary files for each format
            temp_smart_overlay = f"temp_smart_overlay_{timestamp}.pdf"
            temp_inline = f"temp_inline_{timestamp}.pdf"
            temp_traditional = f"temp_traditional_{timestamp}.pdf"
            
            print("🔄 Generating Smart Overlay PDF...")
            smart_generator = SmartOverlayAnnotator(self.original_pdf_path, theme=self.theme)
            smart_generator.create_smart_overlay_pdf(annotations_data, temp_smart_overlay)
            
            print("🔄 Generating Inline PDF...")
            inline_generator = InlinePDFAnnotator(self.original_pdf_path)
            inline_generator.create_inline_annotated_pdf(annotations_data, temp_inline)
            
            print("🔄 Generating Color-Coded Traditional PDF...")
            self._create_color_coded_traditional_pdf(annotations_data, temp_traditional)
            
            print("🔄 Combining all PDFs...")
            self._combine_all_pdfs([temp_smart_overlay, temp_inline, temp_traditional], output_filename)
            
            # Clean up temporary files
            for temp_file in [temp_smart_overlay, temp_inline, temp_traditional]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return output_filename
            
        except Exception as e:
            print(f"Error creating combined PDF: {e}")
            # Clean up any remaining temp files
            for temp_file in [temp_smart_overlay, temp_inline, temp_traditional]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return None
    
    def _create_color_coded_traditional_pdf(self, annotations_data: Dict, output_filename: str):
        """Create traditional PDF with color-coded sections."""
        
        # Create the annotation document with colors
        annotation_buffer = io.BytesIO()
        self._create_color_coded_annotation_document(annotation_buffer, annotations_data)
        
        # Combine with original PDF
        self._combine_pdfs_traditional(annotation_buffer, output_filename)
    
    def _create_color_coded_annotation_document(self, buffer, annotations_data: Dict):
        """Create a comprehensive annotation document with color-coded sections."""
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Define base styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=blue,
            alignment=TA_LEFT
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        story = []
        
        # Title page
        story.append(Paragraph("🎯 COMPREHENSIVE LESSON PLAN ANALYSIS", title_style))
        story.append(Paragraph("AI-Powered Educational Insights with Color-Coded Categories", body_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Color legend
        story.append(Paragraph("🎨 COLOR LEGEND", 
                              ParagraphStyle('LegendTitle', parent=styles['Heading2'], fontSize=14, textColor=blue)))
        
        legend_text = self._create_color_legend(annotations_data)
        story.append(Paragraph(legend_text, body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Lesson info
        if 'lesson_info' in annotations_data:
            info = annotations_data['lesson_info']
            story.append(Paragraph("📋 LESSON INFORMATION", 
                                 ParagraphStyle('InfoTitle', parent=styles['Heading2'], fontSize=12)))
            
            lesson_details = f"""
            <b>PDF File:</b> {info.get('pdf_path', 'N/A')}<br/>
            <b>Analysis Date:</b> {info.get('timestamp', 'N/A')}<br/>
            <b>Theme:</b> {self.theme.title()}<br/>
            <b>Grade Level:</b> {info.get('structure', {}).get('grade_level', 'N/A')}<br/>
            <b>Week/Day:</b> {info.get('structure', {}).get('week', 'N/A')}
            """
            story.append(Paragraph(lesson_details, body_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Main annotations with color coding
        if 'annotations' in annotations_data:
            story.append(PageBreak())
            story.append(Paragraph("🤖 AI ANALYSIS & RECOMMENDATIONS", title_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Parse and format the annotations with colors
            annotation_text = annotations_data['annotations']
            sections = self._parse_annotation_sections(annotation_text)
            
            for section_title, content in sections.items():
                # Determine color for this section
                color_category = self._map_section_to_color_category(section_title)
                section_color = self._rgb_to_reportlab_color(
                    self.section_colors.get(color_category, (0.1, 0.4, 0.8))
                )
                
                # Create colored section style
                colored_section_style = ParagraphStyle(
                    f'ColoredSection_{color_category}',
                    parent=styles['Heading2'],
                    fontSize=12,
                    spaceBefore=15,
                    spaceAfter=10,
                    textColor=section_color,
                    alignment=TA_LEFT
                )
                
                story.append(Paragraph(section_title, colored_section_style))
                
                # Process content to handle lists and formatting
                formatted_content = self._format_content(content)
                story.append(Paragraph(formatted_content, body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Usage statistics
        if 'usage' in annotations_data:
            story.append(PageBreak())
            story.append(Paragraph("📊 ANALYSIS STATISTICS", 
                                 ParagraphStyle('StatsTitle', parent=styles['Heading2'], fontSize=12)))
            usage = annotations_data['usage']
            usage_text = f"""
            <b>Prompt Tokens:</b> {usage.get('prompt_tokens', 'N/A')}<br/>
            <b>Completion Tokens:</b> {usage.get('completion_tokens', 'N/A')}<br/>
            <b>Total Tokens:</b> {usage.get('total_tokens', 'N/A')}
            """
            story.append(Paragraph(usage_text, body_style))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
    
    def _create_color_legend(self, annotations_data: Dict) -> str:
        """Create HTML text for color legend using actual custom definitions."""
        legend_items = []
        
        # Check if we have custom category definitions from the user's session
        parameters_used = annotations_data.get('parameters_used', {})
        custom_definitions = parameters_used.get('custom_category_definitions', {})
        
        if custom_definitions:
            # Use the actual custom definitions from the user's session
            print(f"🎨 Using custom definitions: {custom_definitions}")
            
            # Create legend based on custom definitions and their corresponding colors
            for category, definition in custom_definitions.items():
                color_rgb = self.section_colors.get(category, (0.5, 0.5, 0.5))
                # Convert RGB to hex for HTML
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(color_rgb[0] * 255),
                    int(color_rgb[1] * 255),
                    int(color_rgb[2] * 255)
                )
                legend_items.append(f'<font color="{hex_color}">■</font> <b>{definition}</b>')
        else:
            # Fallback to theme-based definitions
            try:
                themes_path = os.path.join(os.path.dirname(__file__), 'themes.json')
                with open(themes_path, 'r') as f:
                    themes_data = json.load(f)
                
                theme_data = themes_data['themes'].get(self.theme, {})
                category_definitions = theme_data.get('category_definitions', {})
                
                for category, color_rgb in self.section_colors.items():
                    definition = category_definitions.get(category, category.replace('_', ' ').title())
                    # Convert RGB to hex for HTML
                    hex_color = '#{:02x}{:02x}{:02x}'.format(
                        int(color_rgb[0] * 255),
                        int(color_rgb[1] * 255),
                        int(color_rgb[2] * 255)
                    )
                    legend_items.append(f'<font color="{hex_color}">■</font> <b>{definition}</b>')
                    
            except Exception:
                # Final fallback legend
                legend_items = [
                    '<font color="#1ab334">■</font> <b>Student Engagement</b>',
                    '<font color="#e67f0d">■</font> <b>Differentiation Strategies</b>',
                    '<font color="#7f1acc">■</font> <b>Assessment Methods</b>',
                    '<font color="#cc1a1a">■</font> <b>Areas for Improvement</b>',
                    '<font color="#1a66cc">■</font> <b>Pedagogical Strengths</b>',
                    '<font color="#999910">■</font> <b>Resources & Materials</b>',
                    '<font color="#cc1a99">■</font> <b>Extension Activities</b>',
                    '<font color="#1acc99">■</font> <b>Cultural Considerations</b>'
                ]
        
        return '<br/>'.join(legend_items)
    
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
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '*', '•')):
                # Convert to bullet points
                clean_line = line[1:].strip()
                formatted_lines.append(f'• {clean_line}')
            elif line:
                formatted_lines.append(line)
        
        return '<br/>'.join(formatted_lines)
    
    def _combine_pdfs_traditional(self, annotation_buffer, output_filename: str):
        """Combine original PDF with color-coded annotations."""
        try:
            # Open original PDF
            original_pdf = PdfReader(self.original_pdf_path)
            
            # Create annotations PDF from buffer
            annotation_buffer.seek(0)
            annotations_pdf = PdfReader(annotation_buffer)
            
            # Create output PDF
            output_pdf = PdfWriter()
            
            # Add original pages first
            for page_num in range(len(original_pdf.pages)):
                output_pdf.add_page(original_pdf.pages[page_num])
            
            # Add annotation pages
            for page_num in range(len(annotations_pdf.pages)):
                output_pdf.add_page(annotations_pdf.pages[page_num])
            
            # Write combined PDF
            with open(output_filename, 'wb') as output_file:
                output_pdf.write(output_file)
                
        except Exception as e:
            print(f"Error combining PDFs: {e}")
            raise
    
    def _combine_all_pdfs(self, pdf_files: list, output_filename: str):
        """Combine multiple PDF files into one."""
        try:
            output_pdf = PdfWriter()
            
            # Add title page
            self._add_title_page(output_pdf)
            
            # Add each PDF with section dividers
            section_titles = [
                "📱 SMART OVERLAY ANNOTATIONS",
                "📝 INLINE ANNOTATIONS", 
                "📋 COMPREHENSIVE ANALYSIS"
            ]
            
            for i, (pdf_file, section_title) in enumerate(zip(pdf_files, section_titles)):
                if os.path.exists(pdf_file):
                    # Add section divider
                    self._add_section_divider(output_pdf, section_title)
                    
                    # Add PDF content
                    with open(pdf_file, 'rb') as file:
                        pdf_reader = PdfReader(file)
                        for page_num in range(len(pdf_reader.pages)):
                            output_pdf.add_page(pdf_reader.pages[page_num])
            
            # Write final combined PDF
            with open(output_filename, 'wb') as output_file:
                output_pdf.write(output_file)
                
        except Exception as e:
            print(f"Error combining all PDFs: {e}")
            raise
    
    def _add_title_page(self, output_pdf: PdfWriter):
        """Add a title page to the combined PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitlePage',
            parent=styles['Title'],
            fontSize=24,
            textColor=blue,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        story = []
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("🎯 COMPREHENSIVE LESSON PLAN ANALYSIS", title_style))
        story.append(Paragraph("Multi-Format AI-Powered Educational Insights", subtitle_style))
        story.append(Spacer(1, 1*inch))
        
        features = [
            "📱 <b>Smart Overlay</b>: Intelligent annotation placement with color-coded insights",
            "📝 <b>Inline Annotations</b>: Integrated feedback within lesson content", 
            "📋 <b>Comprehensive Analysis</b>: Detailed recommendations with visual color coding"
        ]
        
        for feature in features:
            story.append(Paragraph(feature, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                              styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        title_pdf = PdfReader(buffer)
        output_pdf.add_page(title_pdf.pages[0])
    
    def _add_section_divider(self, output_pdf: PdfWriter, section_title: str):
        """Add a section divider page."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        styles = getSampleStyleSheet()
        divider_style = ParagraphStyle(
            'SectionDivider',
            parent=styles['Title'],
            fontSize=20,
            textColor=blue,
            alignment=TA_CENTER
        )
        
        story = []
        story.append(Spacer(1, 3*inch))
        story.append(Paragraph(section_title, divider_style))
        
        doc.build(story)
        buffer.seek(0)
        
        divider_pdf = PdfReader(buffer)
        output_pdf.add_page(divider_pdf.pages[0])