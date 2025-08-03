import PyPDF2
from typing import List, Dict


class PDFExtractor:
    """Extract text and structure from PDF lesson plans."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages_text = []
        
    def extract_text(self) -> List[str]:
        """Extract text from all pages of the PDF."""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    self.pages_text.append(text)
                    
            return self.pages_text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return []
    
    def get_lesson_structure(self) -> Dict:
        """Analyze the lesson plan structure and extract key components."""
        if not self.pages_text:
            self.extract_text()
            
        structure = {
            "title": "",
            "week": "",
            "day": "",
            "objectives": [],
            "materials": [],
            "activities": [],
            "duration": "",
            "grade_level": ""
        }
        
        # Extract structure from first page if available
        if self.pages_text:
            first_page = self.pages_text[0]
            
            # Extract week and day
            if "SEMANA" in first_page and "Día" in first_page:
                lines = first_page.split('\n')
                for line in lines:
                    if "SEMANA" in line and "Día" in line:
                        structure["week"] = line.strip()
                        break
            
            # Extract grade level
            if "Grado" in first_page:
                lines = first_page.split('\n')
                for line in lines:
                    if "Grado" in line:
                        structure["grade_level"] = line.strip()
                        break
            
            # Extract objectives
            if "Objetivos del estudiante" in first_page:
                lines = first_page.split('\n')
                in_objectives = False
                for line in lines:
                    if "Objetivos del estudiante" in line:
                        in_objectives = True
                        continue
                    elif in_objectives and line.strip().startswith("•"):
                        structure["objectives"].append(line.strip())
                    elif in_objectives and "Materiales" in line:
                        break
        
        return structure