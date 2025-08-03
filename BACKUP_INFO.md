# 📁 AI Lesson Plan Annotator - Backup Information

## 📅 Backup Details
- **Date Created**: $(date)
- **Project Version**: Complete Web Application v1.0
- **Backup Location**: `../ai-lesson-plan-annotate-backup-YYYYMMDD_HHMMSS.tar.gz`

## 📦 What's Included in This Backup

### ✅ Core Application Files
- `app.py` - Flask web application
- `run_app.py` - Application startup script  
- `start_server.py` - Alternative server startup
- `lesson_annotator.py` - Core annotation logic
- `pdf_extractor.py` - PDF text extraction
- `llama_client.py` - Llama AI API integration
- `pdf_annotator.py` - PDF annotation generation
- `annotation_parameters.py` - Parameter presets
- `create_pdf_from_json.py` - Utility script
- `test_server.py` - Server testing script

### 🌐 Web Interface Files
- `templates/` - HTML templates (base, index, results)
- `static/css/style.css` - Custom styling
- `static/js/main.js` - JavaScript functionality

### 📄 Configuration & Documentation
- `requirements.txt` - Python dependencies
- `README.md` - Complete documentation
- `.env` - API key configuration
- `BACKUP_INFO.md` - This file

### 📊 Sample Files & Results
- `fonetica8.pdf` - Original lesson plan sample
- `annotations_*.json` - Sample analysis results
- `annotated_*.pdf` - Sample annotated PDFs

## ❌ What's Excluded from Backup
- `venv/` - Virtual environment (recreate with `pip install -r requirements.txt`)
- `__pycache__/` - Python cache files
- `uploads/` - Temporary upload directory
- `downloads/` - Generated files directory
- `.git/` - Git repository (if any)

## 🔄 How to Restore from Backup

### 1. Extract the Backup
```bash
tar -xzf ai-lesson-plan-annotate-backup-YYYYMMDD_HHMMSS.tar.gz
cd ai-lesson-plan-annotate
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Verify .env file has your API key
cat .env
```

### 4. Create Required Directories
```bash
mkdir -p uploads downloads
```

### 5. Start the Application
```bash
python run_app.py
# Or: python start_server.py
```

### 6. Access Web Interface
Open browser to: `http://127.0.0.1:5000`

## 🔧 System Requirements
- Python 3.8 or higher
- Internet connection for AI API calls
- Modern web browser
- ~50MB disk space for installation

## 🔑 Important Notes
- **API Key**: Ensure your Llama API key is properly configured in `.env`
- **Dependencies**: All Python packages listed in `requirements.txt`
- **Port**: Default runs on port 5000 (configurable)
- **Security**: This is a development setup - use proper WSGI server for production

## 📞 Support
- Check `README.md` for detailed usage instructions
- Run `python test_server.py` to verify installation
- All features tested and working as of backup date

## 🏗️ Project Structure
```
ai-lesson-plan-annotate/
├── app.py                    # Main Flask application
├── run_app.py               # Startup script
├── lesson_annotator.py      # Core logic
├── pdf_extractor.py         # PDF processing
├── llama_client.py          # AI integration
├── pdf_annotator.py         # PDF generation
├── annotation_parameters.py # Configuration
├── templates/               # Web templates
├── static/                  # CSS/JS files
├── requirements.txt         # Dependencies
├── README.md               # Documentation
└── .env                    # API configuration
```

**✅ Backup Complete - Your AI Lesson Plan Annotator is safely preserved!**