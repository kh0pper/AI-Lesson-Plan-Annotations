# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p uploads downloads
```

### Running the Application
```bash
# Start web application (preferred method)
python run_app.py

# Alternative startup
python app.py

# Direct lesson annotation (CLI)
python lesson_annotator.py
```

### Environment Configuration
- Copy `.env.example` to `.env` and add your `LLAMA_API_KEY`
- Web app runs on `http://localhost:5000`

### PDF Generation Scripts
```bash
# Generate different annotation types from existing JSON results
python create_pdf_from_json.py annotations_file.json        # Traditional
python create_inline_pdf.py annotations_file.json           # Inline
python create_overlay_pdf.py annotations_file.json          # Basic overlay
python create_smart_overlay_pdf.py annotations_file.json                    # Smart overlay (recommended)  
python create_smart_overlay_pdf.py annotations_file.json fonetica8.pdf vibrant  # With custom theme
```

### Testing
```bash
# Test server functionality
python test_server.py
```

## Architecture Overview

### Core Components
This is a Flask-based AI lesson plan annotation system with multiple PDF output formats:

- **Flask Web App** (`app.py`): Main web interface with file upload, parameter selection, and download management
- **Lesson Annotator** (`lesson_annotator.py`): Core orchestration - coordinates PDF extraction, AI analysis, and multi-format output generation
- **PDF Processing Pipeline**: 
  - `pdf_extractor.py`: Extracts text and analyzes document structure
  - Multiple annotation generators for different output styles
- **AI Integration**: `llama_client.py` and `enhanced_llama_client.py` for Llama API communication
- **Parameter System** (`annotation_parameters.py`): Preset configurations for different lesson types (kindergarten phonics, general K, Spanish literacy)

### PDF Annotation Types
The system generates four distinct annotation formats:

1. **Smart Overlay** (`smart_overlay_annotator.py`): AI-powered layout analysis with intelligent positioning
2. **Basic Overlay** (`pdf_overlay_annotator.py`): Visual overlays preserving original layout
3. **Inline** (`inline_pdf_annotator.py`): Annotations integrated directly into lesson content
4. **Traditional** (`pdf_annotator.py`): Original lesson + comprehensive analysis appendix

### Data Flow
1. PDF upload → text extraction → structure analysis
2. AI annotation generation using configurable parameters
3. Parallel generation of all four annotation formats
4. Results saved as JSON + multiple PDF outputs

### Parameter Presets
- **kindergarten_phonics**: Multisensory learning focus, phonological awareness
- **general_kindergarten**: Play-based learning, broad engagement
- **spanish_literacy**: Balanced literacy approach for Spanish L1
- **custom**: User-defined parameters via web form

### Color Themes for Smart Overlay
The system supports customizable color schemes for smart overlay annotations:
- **educational** (default): Educational psychology-based colors
- **vibrant**: High contrast colors for maximum visibility
- **pastel**: Soft, gentle colors for easy reading
- **academic**: Professional academic color scheme
- **monochrome**: Grayscale theme for printing
- **warm**: Warm, inviting color palette
- **cool**: Cool, calming color palette
- **custom**: User-defined color categories and meanings

### User-Defined Color Significance
When using the **custom** theme, users can define what each color represents:
- The AI will categorize annotations according to user-defined meanings
- 8 customizable categories with color-coded visual organization
- Example: "Red = Critical Issues", "Green = Strengths", "Blue = Student Engagement"
- Accessible via web interface custom parameters section
- AI adapts annotation categorization to match user definitions

Configure via web interface or command line: `python create_smart_overlay_pdf.py file.json pdf.pdf theme_name`

### File Organization
- `uploads/`: Temporary file storage for processing
- `downloads/`: Generated annotated PDFs and results
- `templates/`: HTML templates for Flask web interface
- `static/`: CSS and JavaScript assets
- Auto-cleanup of temporary files after processing

## Important Notes

### API Requirements
- Requires valid LLAMA_API_KEY in environment
- Uses OpenAI-compatible client for Llama API access
- Token usage tracked and reported in results

### File Handling
- 16MB maximum upload size
- PDF-only input format
- Automatic filename sanitization and unique ID generation
- Comprehensive error handling for PDF processing failures

### Development Considerations
- All PDF generators inherit common patterns but implement different annotation strategies
- Smart overlay annotator represents the most advanced output format with AI-driven layout analysis
- Parameter system allows extensibility for new lesson types and annotation focuses