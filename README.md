# 🎓 AI Lesson Plan Annotator

An intelligent web application that analyzes lesson plans using AI and provides comprehensive annotations and insights with **user authentication**, **custom profiles**, and **premium donation tiers**.

## 🚀 Quick Start

**Can't connect to localhost? Follow these steps:**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API Key**
   ```bash
   cp env_example.txt .env
   # Edit .env and add: OPENAI_API_KEY=your_key_here
   ```

3. **Initialize Database**
   ```bash
   python3 init_db.py
   ```

4. **Start Application**
   ```bash
   python3 app.py
   ```

5. **Visit**: http://localhost:5000

📖 **Detailed Setup**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

## ✨ Features

### 🆓 Free Tier
- **PDF Upload & Analysis**: Upload lesson plan PDFs and get AI-powered insights
- **1 Custom Profile**: Save your annotation preferences
- **5 Annotations/Hour**: Rate-limited usage
- **All PDF Formats**: Smart Overlay, Inline, Traditional, and Comprehensive PDFs

### ⭐ Premium Tier ($5/month donation)
- **10 Custom Profiles**: Save multiple annotation configurations
- **Unlimited Annotations**: No rate limits
- **Priority Processing**: Faster results
- **Billing Management**: Easy subscription control
- **Support Education**: Help keep this tool free for all teachers

### 📱 Core Features
- **Smart Overlay Annotations** 🧠 **REVOLUTIONARY**: Intelligent layout-aware visual overlays with advanced positioning
- **Overlay Annotations**: Visual overlays on the original PDF preserving exact layout
- **Inline Annotations**: Annotations placed directly alongside lesson content for immediate use
- **Traditional Annotations**: Comprehensive analysis appended after the original lesson plan
- **Customizable Parameters**: Choose from presets or create custom annotation guidelines
- **Professional Output**: Generate annotated PDFs with detailed recommendations
- **Web Interface**: User-friendly web application with real-time processing
- **Multiple Presets**: Specialized for kindergarten phonics, general education, and Spanish literacy

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure API Key
Make sure your `.env` file contains your Llama API key:
```
LLAMA_API_KEY=your_api_key_here
```

### 3. Run the Web Application
```bash
# Start the web server
source venv/bin/activate
python run_app.py
```

### 4. Access the Application
Open your browser and go to: `http://localhost:5000`

## 🎯 Usage

### Web Interface
1. **Upload PDF**: Select your lesson plan PDF file (max 16MB)
2. **Choose Preset**: Select an annotation preset that matches your lesson type:
   - **Kindergarten Phonics**: Specialized for phonics lessons with multisensory approach
   - **General Kindergarten**: Play-based learning with general K-level parameters
   - **Spanish Literacy**: Balanced literacy approach for Spanish language arts
   - **Custom**: Define your own parameters and guidelines

3. **Custom Guidelines**: Optionally provide specific instructions for the AI analysis
4. **Process**: Click "Analyze Lesson Plan" and wait for processing
5. **Download**: Get your annotated PDF with comprehensive insights

### Command Line Interface
```bash
# Analyze a single lesson plan
source venv/bin/activate
python lesson_annotator.py

# Create traditional PDF from existing JSON results
python create_pdf_from_json.py annotations_file.json

# Create inline PDF from existing JSON results  
python create_inline_pdf.py annotations_file.json

# Create overlay PDF from existing JSON results
python create_overlay_pdf.py annotations_file.json

# Create smart overlay PDF from existing JSON results (BEST)
python create_smart_overlay_pdf.py annotations_file.json
```

## 📁 Project Structure

```
ai-lesson-plan-annotate/
├── app.py                    # Flask web application
├── run_app.py               # Application startup script
├── lesson_annotator.py      # Core annotation logic
├── pdf_extractor.py         # PDF text extraction
├── llama_client.py          # Llama AI API integration
├── pdf_annotator.py         # PDF annotation generation
├── annotation_parameters.py # Parameter presets and configuration
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   └── results.html
├── static/                  # CSS, JS, and static files
│   ├── css/style.css
│   └── js/main.js
├── uploads/                 # Temporary file uploads
├── downloads/               # Generated annotated PDFs
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Annotation Presets

**Kindergarten Phonics**
- Focus: Phonological awareness, letter-sound correspondence, vocabulary
- Approach: Multisensory learning
- Assessment: Formative observation

**General Kindergarten**
- Focus: Student engagement, differentiated instruction, assessment
- Approach: Play-based learning
- Assessment: Formative

**Spanish Literacy**
- Focus: Reading comprehension, phonemic awareness, cultural context
- Approach: Balanced literacy
- Assessment: Authentic assessment

### Custom Parameters
- **Focus Areas**: Choose specific aspects to analyze
- **Pedagogical Approach**: Select teaching methodology
- **Engagement Level**: Specify desired interaction level
- **Assessment Type**: Choose assessment strategy
- **Language Focus**: Target language development
- **Age Group**: Specify student age range

## 📊 Output

The application generates:

1. **Smart Overlay PDF** 🧠 **REVOLUTIONARY**: Intelligent layout-aware annotations with advanced positioning
2. **Overlay Annotated PDF**: Visual overlays on original PDF preserving exact layout
3. **Inline Annotated PDF**: AI insights placed directly alongside relevant lesson sections  
4. **Traditional Annotated PDF**: Original lesson plan + comprehensive AI analysis at the end
5. **JSON Results**: Complete analysis data for future reference
6. **Web Results**: Interactive results page with all download options

### 🎯 Annotation Types Comparison

**Smart Overlay Annotations** (Highly Recommended) 🧠:
- ✅ Intelligent layout analysis and content detection
- ✅ Priority-based annotation hierarchy
- ✅ Content-aware positioning (objectives near objectives, etc.)
- ✅ Advanced white space detection
- ✅ Enhanced visual design with gradients and icons
- ✅ Color-coded by insight type with smart spacing
- ✅ Perfect for maintaining document integrity

**Overlay Annotations** 🎯:
- ✅ Preserves original PDF layout exactly
- ✅ Visual annotation boxes in margins
- ✅ Color-coded by insight type
- ✅ Perfect for maintaining document integrity
- ✅ Easy to read while teaching

**Inline Annotations**:
- ✅ Insights placed next to relevant lesson sections
- ✅ Good for immediate classroom implementation
- ✅ Focused, actionable suggestions
- ✅ Restructured content format

**Traditional Annotations**:
- ✅ Comprehensive analysis report
- ✅ Detailed explanations and examples
- ✅ Good for lesson planning and reflection
- ✅ Complete pedagogical insights

### Annotation Categories

- 📚 **Pedagogical Strengths**: Effective teaching strategies
- 🎯 **Student Engagement**: Participation enhancement opportunities
- 📊 **Assessment Suggestions**: Formative and summative strategies
- 🔄 **Differentiation Strategies**: Multi-level accommodation
- 💡 **Resource Optimization**: Better use of materials and time
- ➕ **Extension Activities**: Additional learning opportunities
- 🔧 **Areas for Improvement**: Constructive enhancement suggestions
- 🌍 **Cultural/Linguistic Considerations**: Language-specific insights

## 🛠️ Technical Details

- **Backend**: Flask web framework
- **AI Integration**: Llama API via OpenAI-compatible client
- **PDF Processing**: PyPDF2 for reading, ReportLab for generation
- **Frontend**: Bootstrap 5 with custom styling
- **File Handling**: Secure upload with validation

## 📝 Example Usage

1. Upload `fonetica8.pdf` (Spanish kindergarten phonics lesson)
2. Select "Kindergarten Phonics" preset
3. Add custom guideline: "Focus on multisensory activities and differentiation"
4. Process and download annotated PDF with detailed AI insights

## ⚠️ Important Notes

- Maximum file size: 16MB
- Supported format: PDF only
- Processing time: ~30-60 seconds per file
- Files are automatically cleaned up after processing
- API usage is tracked and displayed in results

## 🔒 Security

- File validation and sanitization
- Temporary file cleanup
- Secure filename handling
- Environment variable configuration

## 🤝 Support

For issues or questions, please refer to the application's built-in help or check the processing logs for detailed error information.