import os
import uuid
import stripe
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import json

from lesson_annotator import LessonPlanAnnotator
from annotation_parameters import ParameterPresets, AnnotationParameters, parameters_to_dict
from models import db, User, AnnotationProfile, UsageRecord
from forms import RegistrationForm, LoginForm, ProfileForm
from stripe_integration import StripeService, get_stripe_public_key

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "ai_annotator.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure upload and download directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Landing page for anonymous users, upload page for authenticated users."""
    if not current_user.is_authenticated:
        # Show landing page for anonymous users
        return render_template('landing.html', stripe_public_key=get_stripe_public_key())
    
    # Show upload interface for authenticated users
    presets = ParameterPresets.get_available_presets()
    user_profiles = []
    
    # Load user's saved profiles if logged in
    user_profiles = AnnotationProfile.query.filter_by(user_id=current_user.id).order_by(AnnotationProfile.is_default.desc(), AnnotationProfile.name).all()
    
    # Auto-load default profile if exists
    default_profile = next((p for p in user_profiles if p.is_default), None)
    if default_profile:
        session['default_profile_data'] = default_profile.to_dict()
    
    return render_template('index.html', presets=presets, user_profiles=user_profiles)

@app.route('/app')
@login_required
def app_interface():
    """Upload interface for authenticated users (alternative route)."""
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload and annotation parameters."""
    
    # Check rate limits for logged-in users
    if not current_user.can_run_annotation():
        flash(f'Rate limit exceeded. Free accounts can run {current_user.get_hourly_usage_limit()} annotations per hour. Consider becoming a premium supporter for unlimited usage!')
        return redirect(url_for('donate'))
    
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
            # Record usage for rate limiting (if user is logged in)
            if current_user.is_authenticated:
                usage_record = UsageRecord(
                    user_id=current_user.id,
                    pdf_filename=filename,
                    tokens_used=result.get("usage", {}).get("total_tokens"),
                    success=True
                )
                db.session.add(usage_record)
                db.session.commit()
            
            # Move annotated PDFs to downloads folder
            download_files = {}
            
            # Combined annotated PDF (primary output)
            combined_pdf_path = result.get("combined_annotated_pdf")
            if combined_pdf_path and os.path.exists(combined_pdf_path):
                combined_filename = f"comprehensive_{unique_id}_{filename}"
                combined_path = os.path.join(app.config['DOWNLOAD_FOLDER'], combined_filename)
                os.rename(combined_pdf_path, combined_path)
                download_files['combined'] = combined_filename
            
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
            
            # Overlay annotated PDF
            overlay_pdf_path = result.get("overlay_annotated_pdf")
            if overlay_pdf_path and os.path.exists(overlay_pdf_path):
                overlay_filename = f"overlay_annotated_{unique_id}_{filename}"
                overlay_path = os.path.join(app.config['DOWNLOAD_FOLDER'], overlay_filename)
                os.rename(overlay_pdf_path, overlay_path)
                download_files['overlay'] = overlay_filename
            
            # Smart overlay annotated PDF
            smart_overlay_pdf_path = result.get("smart_overlay_pdf")
            if smart_overlay_pdf_path and os.path.exists(smart_overlay_pdf_path):
                smart_overlay_filename = f"smart_overlay_{unique_id}_{filename}"
                smart_overlay_path = os.path.join(app.config['DOWNLOAD_FOLDER'], smart_overlay_filename)
                os.rename(smart_overlay_pdf_path, smart_overlay_path)
                download_files['smart_overlay'] = smart_overlay_filename
                
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
        import traceback
        error_details = traceback.format_exc()
        print(f"🚨 Processing Error: {str(e)}")
        print(f"📋 Full traceback:\n{error_details}")
        flash(f'Error processing file: {str(e)}. Please check the server logs for details.')
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
            "age_group": form_data.get('age_group', '5-6 years'),
            "annotation_theme": form_data.get('annotation_theme', 'educational')
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
    
    # Add annotation theme (always available regardless of preset)
    parameters["annotation_theme"] = form_data.get('annotation_theme', 'educational')
    
    # Add custom category definitions if using custom theme
    if form_data.get('annotation_theme') == 'custom':
        custom_categories = {}
        for i in range(1, 9):  # category1 through category8
            category_key = f'category{i}'
            definition = form_data.get(f'category{i}_definition', '').strip()
            if definition:
                custom_categories[category_key] = definition
        if custom_categories:
            parameters["custom_category_definitions"] = custom_categories
    
    # Add custom guidelines if provided
    if custom_guidelines:
        parameters["custom_guidelines"] = custom_guidelines
    
    return parameters


# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created successfully for {form.username.data}!')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.username}!')
            
            # Redirect to next page or index
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


# Profile Management Routes
@app.route('/profiles')
@login_required
def profiles():
    """Display user's annotation profiles."""
    user_profiles = AnnotationProfile.query.filter_by(user_id=current_user.id).order_by(
        AnnotationProfile.is_default.desc(), 
        AnnotationProfile.name
    ).all()
    
    return render_template('profiles.html', profiles=user_profiles)


@app.route('/save_profile', methods=['POST'])
@login_required
def save_profile():
    """Save current form settings as a profile."""
    try:
        profile_name = request.form.get('profile_name', '').strip()
        profile_description = request.form.get('profile_description', '').strip()
        set_as_default = request.form.get('set_as_default') == 'on'
        
        if not profile_name:
            return jsonify({'success': False, 'error': 'Profile name is required'})
        
        # Check profile limits
        if not current_user.can_create_profile():
            limit = current_user.get_profile_limit()
            return jsonify({
                'success': False, 
                'error': f'Profile limit reached. {"Premium supporters" if limit > 1 else "Free accounts"} can save up to {limit} profile{"s" if limit > 1 else ""}. Consider upgrading to save more profiles!'
            })
        
        # Check if profile name already exists for this user
        existing = AnnotationProfile.query.filter_by(
            user_id=current_user.id, 
            name=profile_name
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Profile name already exists'})
        
        # Create new profile from form data
        profile = AnnotationProfile.from_form_data(
            user_id=current_user.id,
            name=profile_name,
            description=profile_description,
            form_data=request.form
        )
        
        # Handle default profile setting
        if set_as_default:
            # Remove default from other profiles
            AnnotationProfile.query.filter_by(
                user_id=current_user.id, 
                is_default=True
            ).update({'is_default': False})
            profile.is_default = True
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile saved successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/profile/<int:profile_id>')
@login_required
def get_profile(profile_id):
    """Get profile data for loading into form."""
    profile = AnnotationProfile.query.filter_by(
        id=profile_id, 
        user_id=current_user.id
    ).first()
    
    if not profile:
        return jsonify({'success': False, 'error': 'Profile not found'})
    
    return jsonify({'success': True, 'profile': profile.to_dict()})


@app.route('/load_profile/<int:profile_id>')
@login_required
def load_profile(profile_id):
    """Load a profile and redirect to main page."""
    profile = AnnotationProfile.query.filter_by(
        id=profile_id, 
        user_id=current_user.id
    ).first()
    
    if not profile:
        flash('Profile not found')
        return redirect(url_for('profiles'))
    
    # Store profile data in session for form population
    session['loaded_profile_data'] = profile.to_dict()
    flash(f'Profile "{profile.name}" loaded successfully!')
    return redirect(url_for('index'))


@app.route('/set_default_profile/<int:profile_id>')
@login_required
def set_default_profile(profile_id):
    """Set a profile as default."""
    profile = AnnotationProfile.query.filter_by(
        id=profile_id, 
        user_id=current_user.id
    ).first()
    
    if not profile:
        flash('Profile not found')
        return redirect(url_for('profiles'))
    
    # Remove default from other profiles
    AnnotationProfile.query.filter_by(
        user_id=current_user.id, 
        is_default=True
    ).update({'is_default': False})
    
    # Set this profile as default
    profile.is_default = True
    db.session.commit()
    
    flash(f'Profile "{profile.name}" set as default!')
    return redirect(url_for('profiles'))


@app.route('/delete_profile/<int:profile_id>')
@login_required
def delete_profile(profile_id):
    """Delete a profile."""
    profile = AnnotationProfile.query.filter_by(
        id=profile_id, 
        user_id=current_user.id
    ).first()
    
    if not profile:
        flash('Profile not found')
        return redirect(url_for('profiles'))
    
    profile_name = profile.name
    db.session.delete(profile)
    db.session.commit()
    
    flash(f'Profile "{profile_name}" deleted successfully!')
    return redirect(url_for('profiles'))


# Stripe/Donation Routes
@app.route('/donate')
def donate():
    """Donation page with premium tier information."""
    return render_template('donate.html', stripe_public_key=get_stripe_public_key())


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe Checkout session for subscription."""
    try:
        success_url = url_for('donation_success', _external=True)
        cancel_url = url_for('donate', _external=True)
        
        checkout_session = StripeService.create_checkout_session(
            current_user, success_url, cancel_url
        )
        
        if checkout_session:
            return redirect(checkout_session.url, code=303)
        else:
            flash('Error creating checkout session. Please try again.')
            return redirect(url_for('donate'))
            
    except Exception as e:
        current_app.logger.error(f"Checkout session error: {e}")
        flash('Error processing donation. Please try again.')
        return redirect(url_for('donate'))


@app.route('/donation-success')
@login_required
def donation_success():
    """Handle successful donation."""
    flash('Thank you for your donation! Your premium features will be activated shortly.')
    return redirect(url_for('index'))


@app.route('/billing-portal')
@login_required
def billing_portal():
    """Redirect to Stripe billing portal."""
    try:
        return_url = url_for('donate', _external=True)
        portal_session = StripeService.create_billing_portal_session(current_user, return_url)
        
        if portal_session:
            return redirect(portal_session.url, code=303)
        else:
            flash('Error accessing billing portal. Please contact support.')
            return redirect(url_for('donate'))
            
    except Exception as e:
        current_app.logger.error(f"Billing portal error: {e}")
        flash('Error accessing billing portal. Please try again.')
        return redirect(url_for('donate'))


@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        # Handle different event types
        if event['type'] == 'customer.subscription.created':
            StripeService.handle_subscription_created(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            StripeService.handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            StripeService.handle_subscription_deleted(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            StripeService.handle_invoice_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            StripeService.handle_invoice_payment_failed(event['data']['object'])
        
        return jsonify({'status': 'success'})
        
    except ValueError as e:
        current_app.logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        current_app.logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook error'}), 500


if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5001)