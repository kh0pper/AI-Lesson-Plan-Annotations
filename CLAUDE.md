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

# Start the Flask application
python3 app.py

# Test template rendering (useful after making template changes)
python3 test_template_render.py

# Command line annotation (bypasses web interface)
python3 lesson_annotator.py
```

### Database Management
```bash
# Initialize fresh database
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

### User Flow
1. User registers/logs in via Flask-Login
2. Uploads PDF (max 16MB, validated)
3. Selects annotation preset or creates custom parameters
4. System processes via AI client and generates multiple PDF formats
5. User downloads annotated PDFs and can save profiles for reuse

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

- Database uses SQLite with no migration system - schema changes require `init_db.py`
- Stripe webhooks must be configured for production subscription handling
- All PDF processing is synchronous - consider async for large files
- User profiles store JSON data for annotation parameters
- Rate limiting uses in-memory storage - not suitable for multi-instance deployment