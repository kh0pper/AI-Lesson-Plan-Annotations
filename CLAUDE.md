# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered lesson plan annotation web application built with Flask. The app allows teachers to upload PDF lesson plans and receive AI-generated pedagogical insights and recommendations. It features user authentication, custom annotation profiles, subscription management, and multiple PDF output formats.

## Key Commands

### Development & Testing
```bash
# Install dependencies (required before first run)
pip install -r requirements.txt

# Initialize database (run once after fresh clone)
python3 init_db.py

# Start the Flask application (will run on port 5001 by default)
python3 app.py

# Alternative: Start Flask with specific settings
python3 -m flask --app app run --host=0.0.0.0 --port=8080 --debug

# Test specific components
python3 test_auth_system.py          # Test user authentication
python3 test_template_render.py      # Test template rendering
python3 test_profiles.py             # Test profile management
python3 test_registration.py         # Test user registration

# Command line annotation (bypasses web interface)
python3 lesson_annotator.py
```

### Database Management
```bash
# Initialize fresh database (creates ai_annotator.db)
python3 init_db.py

# No migrations system - database schema changes require manual init_db.py run
```

## Architecture Overview

### Core Components

**Flask Web Application** (`app.py`):
- User authentication with Flask-Login
- File upload handling with validation
- Stripe integration for subscriptions
- Rate limiting for free tier users
- Profile management system

**AI Integration** (`llama_client.py`, `demo_ai_client.py`):
- Uses Llama API for lesson plan analysis
- Factory pattern for client creation based on API key availability
- Enhanced error handling with user-friendly messages

**PDF Processing Pipeline**:
1. `pdf_extractor.py` - Extract text and structure from uploaded PDFs
2. `lesson_annotator.py` - Core orchestration of the annotation process
3. Multiple PDF generators for different output formats:
   - `pdf_annotator.py` - Traditional format (original + analysis)
   - `inline_pdf_annotator.py` - Inline annotations within content
   - `pdf_overlay_annotator.py` - Visual overlay annotations
   - `smart_overlay_annotator.py` - Intelligent layout-aware overlays
   - `combined_pdf_annotator.py` - Comprehensive multi-format output

**Database Models** (`models.py`):
- `User` - Authentication, subscription status, usage tracking
- `AnnotationProfile` - Custom user annotation preferences
- `UsageRecord` - Rate limiting and usage analytics

**Subscription System** (`stripe_integration.py`):
- Stripe webhook handling for subscription lifecycle
- Two-tier system: Free (1 profile, 5/hour) vs Premium (10 profiles, unlimited)

### Configuration

**Environment Variables** (`.env`):
- `LLAMA_API_KEY` - Required for AI functionality
- `STRIPE_*` keys - Required for subscription features
- `FLASK_SECRET_KEY` - Session management

**Annotation Presets** (`annotation_parameters.py`):
- Predefined parameter sets for different lesson types
- Extensible system for custom annotation guidelines

## Important Implementation Details

### Authentication-Based Access Control
- **Anonymous users**: See landing page with registration/login options and feature overview
- **Authenticated users**: Access full upload interface and annotation functionality
- Landing page (`templates/landing.html`) showcases features and pricing tiers
- Upload endpoint protected with `@login_required` decorator

### User Flow
1. Anonymous users see landing page → register/login required
2. Authenticated users access upload interface directly
3. User uploads PDF (max 16MB, validated)
4. Selects annotation preset or creates custom parameters
5. System processes via AI client and generates multiple PDF formats
6. User downloads annotated PDFs and can save profiles for reuse

### Rate Limiting
- Free users: 5 annotations per hour via `flask-limiter`
- Premium users: Unlimited access
- Usage tracked in `UsageRecord` model

### File Handling
- Secure upload with `werkzeug.utils.secure_filename`
- Temporary files in `uploads/` directory
- Generated PDFs in `downloads/` directory
- Automatic cleanup after processing

### Error Handling
- AI client provides detailed error messages for API issues
- Template validation prevents Flask BuildError issues
- Database relationship cascades handle user deletion

### API Key Management
- Factory pattern in `create_ai_client()` checks for valid keys
- Demo mode removed - requires real API key to function
- Clear error messages guide users to obtain proper credentials

## Critical Notes

- **Port Configuration**: App runs on port 5001 by default (changed from 5000 to avoid conflicts)
- **Database**: Uses SQLite with no migration system - schema changes require `init_db.py`
- **Authentication Required**: Anonymous users cannot access upload functionality
- **Stripe Webhooks**: Must be configured for production subscription handling
- **Processing**: All PDF processing is synchronous - consider async for large files
- **Profile Storage**: User profiles store JSON data for annotation parameters
- **Rate Limiting**: Uses in-memory storage - not suitable for multi-instance deployment
- **API Keys**: Real Llama/OpenAI API key required - demo mode has been removed

## Development Notes

- Flask app automatically creates database tables on startup via `db.create_all()`
- Test files available for major components (auth, profiles, templates, registration)
- Landing page template provides comprehensive marketing/onboarding experience
- User authentication integrated throughout with Flask-Login session management