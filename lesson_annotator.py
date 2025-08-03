import os
import json
from datetime import datetime
from typing import Dict, Optional
from pdf_extractor import PDFExtractor
from llama_client import LlamaAIClient
from enhanced_llama_client import EnhancedLlamaAIClient
from annotation_parameters import ParameterPresets, parameters_to_dict
from pdf_annotator import PDFAnnotationGenerator
from inline_pdf_annotator import InlinePDFAnnotator


class LessonPlanAnnotator:
    """Main class for AI-powered lesson plan annotation."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf_extractor = PDFExtractor(pdf_path)
        self.ai_client = LlamaAIClient()
        self.enhanced_ai_client = EnhancedLlamaAIClient()
        self.lesson_content = ""
        self.lesson_structure = {}
        self.annotations = {}
        
    def process_lesson_plan(self, parameter_preset: str = "kindergarten_phonics") -> Dict:
        """Complete workflow to process and annotate a lesson plan using presets."""
        parameters = self._get_parameters(parameter_preset)
        return self.process_lesson_plan_with_custom_params(parameters)
    
    def process_lesson_plan_with_custom_params(self, parameters: Dict) -> Dict:
        """Complete workflow to process and annotate a lesson plan."""
        
        print("🔍 Extracting PDF content...")
        success = self._extract_content()
        if not success:
            return {"success": False, "error": "Failed to extract PDF content"}
        
        print("📋 Analyzing lesson structure...")
        self._analyze_structure()
        
        print("🎯 Using provided annotation parameters...")
        
        print("🤖 Generating AI annotations...")
        annotation_result = self._generate_annotations(parameters)
        
        if annotation_result["success"]:
            print("📝 Annotations generated successfully!")
            result = {
                "success": True,
                "lesson_info": {
                    "pdf_path": self.pdf_path,
                    "structure": self.lesson_structure,
                    "parameters_used": parameters,
                    "timestamp": datetime.now().isoformat()
                },
                "annotations": annotation_result["annotations"],
                "usage": annotation_result.get("usage", {}),
                "parameters_used": parameters
            }
            
            # Save results
            self._save_results(result)
            
            # Generate both traditional and inline annotated PDFs
            print("📄 Creating annotated PDFs...")
            annotated_pdf = self._create_annotated_pdf(result)
            inline_pdf = self._create_inline_annotated_pdf(result)
            
            if annotated_pdf:
                result["annotated_pdf"] = annotated_pdf
                print(f"📑 Traditional annotated PDF saved as: {annotated_pdf}")
            
            if inline_pdf:
                result["inline_annotated_pdf"] = inline_pdf
                print(f"📑 Inline annotated PDF saved as: {inline_pdf}")
            
            return result
        else:
            return {
                "success": False,
                "error": annotation_result["error"]
            }
    
    def _extract_content(self) -> bool:
        """Extract text content from PDF."""
        try:
            pages = self.pdf_extractor.extract_text()
            if pages:
                self.lesson_content = "\n\n".join(pages)
                return True
            return False
        except Exception as e:
            print(f"Error extracting content: {e}")
            return False
    
    def _analyze_structure(self):
        """Analyze and extract lesson plan structure."""
        self.lesson_structure = self.pdf_extractor.get_lesson_structure()
    
    def _get_parameters(self, preset: str) -> Dict:
        """Get annotation parameters based on preset."""
        if preset == "kindergarten_phonics":
            params = ParameterPresets.kindergarten_phonics()
        elif preset == "general_kindergarten":
            params = ParameterPresets.general_kindergarten()
        elif preset == "spanish_literacy":
            params = ParameterPresets.spanish_literacy()
        else:
            params = ParameterPresets.kindergarten_phonics()  # default
        
        return parameters_to_dict(params)
    
    def _generate_annotations(self, parameters: Dict) -> Dict:
        """Generate AI annotations using the Llama API."""
        return self.ai_client.generate_annotations(self.lesson_content, parameters)
    
    def _save_results(self, results: Dict):
        """Save annotation results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"annotations_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to {filename}")
        except Exception as e:
            print(f"Warning: Could not save results to file: {e}")
    
    def _create_annotated_pdf(self, results: Dict) -> Optional[str]:
        """Create annotated PDF with AI insights."""
        try:
            generator = PDFAnnotationGenerator(self.pdf_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"annotated_{os.path.basename(self.pdf_path).replace('.pdf', '')}_{timestamp}.pdf"
            
            annotated_pdf = generator.create_annotated_pdf(results, output_filename)
            return annotated_pdf
            
        except Exception as e:
            print(f"Warning: Could not create annotated PDF: {e}")
            return None
    
    def _create_inline_annotated_pdf(self, results: Dict) -> Optional[str]:
        """Create inline annotated PDF with AI insights."""
        try:
            generator = InlinePDFAnnotator(self.pdf_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"inline_{os.path.basename(self.pdf_path).replace('.pdf', '')}_{timestamp}.pdf"
            
            inline_pdf = generator.create_inline_annotated_pdf(results, output_filename)
            return inline_pdf
            
        except Exception as e:
            print(f"Warning: Could not create inline annotated PDF: {e}")
            return None
    
    def get_lesson_summary(self) -> Dict:
        """Get a summary of the lesson plan structure."""
        return {
            "pdf_path": self.pdf_path,
            "structure": self.lesson_structure,
            "content_length": len(self.lesson_content),
            "pages_extracted": len(self.pdf_extractor.pages_text)
        }


def main():
    """Main function to run the annotation app."""
    print("🎓 AI Lesson Plan Annotator")
    print("=" * 40)
    
    # Check if PDF exists
    pdf_path = "fonetica8.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Initialize annotator
    annotator = LessonPlanAnnotator(pdf_path)
    
    # Show available presets
    presets = ParameterPresets.get_available_presets()
    print("\nAvailable annotation presets:")
    for preset, description in presets.items():
        print(f"  • {preset}: {description}")
    
    # Use kindergarten_phonics preset (best fit for this lesson)
    preset = "kindergarten_phonics"
    print(f"\n🎯 Using preset: {preset}")
    
    # Process the lesson plan
    result = annotator.process_lesson_plan(preset)
    
    if result["success"]:
        print("\n✅ Annotation Complete!")
        print(f"📊 Tokens used: {result['usage'].get('total_tokens', 'N/A')}")
        
        if "annotated_pdf" in result:
            print(f"📑 Annotated PDF: {result['annotated_pdf']}")
            print("\n💡 Your lesson plan has been analyzed and an annotated PDF has been created!")
            print("   The annotated PDF contains the original lesson plan followed by detailed AI insights.")
        
        print("\n" + "=" * 60)
        print("ANNOTATIONS SUMMARY:")
        print("=" * 60)
        # Show abbreviated version since full annotations are in the PDF
        annotations = result["annotations"]
        if len(annotations) > 500:
            print(annotations[:500] + "...")
            print(f"\n[Full annotations available in the generated PDF: {result.get('annotated_pdf', 'N/A')}]")
        else:
            print(annotations)
    else:
        print(f"\n❌ Error: {result['error']}")


if __name__ == "__main__":
    main()