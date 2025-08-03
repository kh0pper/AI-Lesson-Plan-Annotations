import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import json

from lesson_annotator import LessonPlanAnnotator
from annotation_parameters import ParameterPresets, AnnotationParameters, parameters_to_dict

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and download directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main upload page."""
    presets = ParameterPresets.get_available_presets()
    return render_template('index.html', presets=presets)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and annotation parameters."""
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if not file or not allowed_file(file.filename):
        flash('Please upload a PDF file')
        return redirect(request.url)
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())[:8]
    timestamped_filename = f"{unique_id}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], timestamped_filename)
    file.save(file_path)
    
    # Get annotation parameters
    preset = request.form.get('preset', 'kindergarten_phonics')
    custom_guidelines = request.form.get('custom_guidelines', '').strip()
    
    # Get custom parameters if provided
    parameters = _get_annotation_parameters(preset, request.form, custom_guidelines)
    
    try:
        # Process the lesson plan
        annotator = LessonPlanAnnotator(file_path)
        result = annotator.process_lesson_plan_with_custom_params(parameters)
        
        if result["success"]:
            # Move annotated PDFs to downloads folder
            download_files = {}
            
            # Traditional annotated PDF
            annotated_pdf_path = result.get("annotated_pdf")
            if annotated_pdf_path and os.path.exists(annotated_pdf_path):
                download_filename = f"annotated_{unique_id}_{filename}"
                download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], download_filename)
                os.rename(annotated_pdf_path, download_path)
                download_files['traditional'] = download_filename
            
            # Inline annotated PDF  
            inline_pdf_path = result.get("inline_annotated_pdf")
            if inline_pdf_path and os.path.exists(inline_pdf_path):
                inline_filename = f"inline_annotated_{unique_id}_{filename}"
                inline_path = os.path.join(app.config['DOWNLOAD_FOLDER'], inline_filename)
                os.rename(inline_pdf_path, inline_path)
                download_files['inline'] = inline_filename
                
                # Save processing results
                results_file = os.path.join(app.config['DOWNLOAD_FOLDER'], f"results_{unique_id}.json")
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                return render_template('results.html', 
                                     success=True,
                                     download_files=download_files,
                                     unique_id=unique_id,
                                     original_filename=filename,
                                     annotations=result["annotations"],
                                     usage=result.get("usage", {}),
                                     parameters=parameters)
            else:
                flash('Error generating annotated PDF')
                return redirect(url_for('index'))
        else:
            flash(f'Error processing file: {result.get("error", "Unknown error")}')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/download/<filename>')
def download_file(filename):
    """Download annotated PDF file."""
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/api/presets')
def get_presets():
    """API endpoint to get available parameter presets."""
    presets = ParameterPresets.get_available_presets()
    return jsonify(presets)

@app.route('/api/preset/<preset_name>')
def get_preset_details(preset_name):
    """API endpoint to get details for a specific preset."""
    try:
        if preset_name == "kindergarten_phonics":
            params = ParameterPresets.kindergarten_phonics()
        elif preset_name == "general_kindergarten":
            params = ParameterPresets.general_kindergarten()
        elif preset_name == "spanish_literacy":
            params = ParameterPresets.spanish_literacy()
        else:
            params = ParameterPresets.kindergarten_phonics()
        
        return jsonify(parameters_to_dict(params))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def _get_annotation_parameters(preset: str, form_data, custom_guidelines: str) -> dict:
    """Extract annotation parameters from form data."""
    
    # Start with preset
    if preset == "custom":
        # Build custom parameters from form
        focus_areas = []
        for key in form_data:
            if key.startswith('focus_area_') and form_data[key]:
                focus_areas.append(form_data[key])
        
        if not focus_areas:
            focus_areas = ["Student Learning", "Engagement", "Assessment"]
        
        parameters = {
            "focus_areas": focus_areas,
            "pedagogical_approach": form_data.get('pedagogical_approach', 'Constructivist'),
            "engagement_level": form_data.get('engagement_level', 'High'),
            "assessment_type": form_data.get('assessment_type', 'Formative'),
            "differentiation": form_data.get('differentiation', 'Multi-level'),
            "language_focus": form_data.get('language_focus', 'Spanish'),
            "age_group": form_data.get('age_group', '5-6 years')
        }
    else:
        # Use preset and convert to dict
        if preset == "kindergarten_phonics":
            params = ParameterPresets.kindergarten_phonics()
        elif preset == "general_kindergarten":
            params = ParameterPresets.general_kindergarten()
        elif preset == "spanish_literacy":
            params = ParameterPresets.spanish_literacy()
        else:
            params = ParameterPresets.kindergarten_phonics()
        
        parameters = parameters_to_dict(params)
    
    # Add custom guidelines if provided
    if custom_guidelines:
        parameters["custom_guidelines"] = custom_guidelines
    
    return parameters

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)