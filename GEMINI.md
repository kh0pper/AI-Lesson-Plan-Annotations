# GEMINI.md

## Project Overview

This is an AI-powered lesson plan annotation web application built with Flask. The app allows teachers to upload PDF lesson plans and receive AI-generated pedagogical insights and recommendations. It features user authentication, custom annotation profiles, Stripe subscription management, secure admin panel, and multiple PDF output formats with persistent PostgreSQL database storage.

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
python3 test_webhook.py              # Test Stripe webhook endpoint
python3 test_billing_portal.py       # Test Stripe billing portal
python3 quick_portal_test.py         # Quick Stripe portal validation

# Manual subscription management
python3 update_subscription.py       # Update user subscription status

# Command line annotation (bypasses web interface)
python3 lesson_annotator.py
```

## Database Management
```bash
# Initialize fresh database (creates ai_annotator.db locally, or initializes PostgreSQL tables)
python3 init_db.py

# Grant alpha tester access (local database)
python3 grant_alpha_access.py user@email.com

# Manage users on remote Render deployment
python3 manage_render_users.py list https://your-app.onrender.com
python3 manage_render_users.py grant https://your-app.onrender.com user@email.com

# No migrations system - database schema changes require manual init_db.py run
# Production uses PostgreSQL via DATABASE_URL, development uses SQLite fallback
```

### Deployment
```bash
# Deploy to Render (see DEPLOYMENT.md for full guide)
# 1. Push code to GitHub
# 2. Connect GitHub repo to Render
# 3. Set environment variables in Render dashboard
# 4. Deploy automatically

# Health check endpoint
curl https://your-app.onrender.com/health
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
- `User` - Authentication, subscription status, usage tracking, alpha tester detection
- `AnnotationProfile` - Custom user annotation preferences (JSON storage)
- `UsageRecord` - Rate limiting and usage analytics
- Automatic PostgreSQL detection via `DATABASE_URL` environment variable
- SQLite fallback for local development

**Subscription System** (`stripe_integration.py`):
- Stripe webhook handling for subscription lifecycle
- Stripe billing portal integration for subscription management
- Two-tier system: Free (1 profile, 5/hour) vs Premium (10 profiles, unlimited)
- Webhook endpoints handle subscription created/updated/deleted events
- Customer portal must be configured in Stripe Dashboard for billing management

**Admin Panel** (`templates/admin.html`, admin routes in `app.py`):
- Secure multi-layer authentication (user login + admin whitelist + optional password)
- User management interface with search/filtering capabilities
- Alpha tester management system with API endpoints
- Admin action logging with IP tracking
- Web interface accessible at `/admin` for authorized users only

### Configuration

**Environment Variables** (`.env`):
- `LLAMA_API_KEY` - Required for AI functionality (format: `LLM|userid|apikey`)
- `DATABASE_URL` - PostgreSQL connection string for persistent storage (production)
- `STRIPE_*` keys - Required for subscription features
- `FLASK_SECRET_KEY` - Session management
- `ADMIN_EMAILS` - Comma-separated admin email whitelist
- `ADMIN_API_KEY` - API key for admin endpoints
- `ADMIN_PASSWORD` - Optional additional admin password
- `ADMIN_IP_WHITELIST` - Optional IP restriction for admin API

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
- **Database Persistence**:
  - **Production**: Requires `DATABASE_URL` (PostgreSQL) for persistent storage
  - **Development**: Falls back to SQLite (ephemeral on cloud platforms)
  - No migration system - schema changes require `init_db.py`
- **Authentication Required**: Anonymous users see landing page, must login to access tools
- **Admin Panel Security**:
  - Multi-layer authentication: user login + admin email whitelist + optional password
  - Access via `/admin` route requires `ADMIN_EMAILS` environment variable
  - API endpoints secured with `ADMIN_API_KEY` header authentication
  - All admin actions logged with user and IP tracking
- **Stripe Configuration**:
  - Webhooks must be configured at `/stripe-webhook` endpoint in production
  - Customer Portal must be configured in Stripe Dashboard before billing management works
  - Test/Live mode API keys must match customer data (test customers need test keys, live customers need live keys)
- **Processing**: All PDF processing is synchronous - consider async for large files
- **Profile Storage**: User profiles store JSON data for annotation parameters
- **Rate Limiting**: Uses in-memory storage - not suitable for multi-instance deployment
- **API Keys**: Real Llama API key required - demo mode has been removed

## Stripe Integration Troubleshooting

### Common Issues:
- **405 Method Not Allowed**: Check webhook endpoint accepts POST requests
- **Billing Portal Error**: Ensure Customer Portal is configured in Stripe Dashboard
- **Authentication Errors**: Verify API key mode (test/live) matches customer data mode
- **Webhook Failures**: Check `STRIPE_WEBHOOK_SECRET` environment variable is set correctly

### Required Stripe Setup:
1. Configure Customer Portal in Stripe Dashboard (`Settings > Billing > Customer Portal`)
2. Set webhook endpoint to `https://your-domain.com/stripe-webhook`
3. Subscribe to events: `customer.subscription.*`, `invoice.payment.*`
4. Ensure live mode keys are used for production deployment

## Development Notes

- Flask app automatically creates database tables on startup via `init_database()`
- Database URL detection: PostgreSQL for production (`DATABASE_URL`), SQLite for development
- Test files available for major components (auth, profiles, templates, registration)
- Landing page template provides comprehensive marketing/onboarding experience
- User authentication integrated throughout with Flask-Login session management
- Admin panel provides user management with search/filter capabilities
- Alpha tester system allows premium access without Stripe subscriptions

## Alpha Tester Management

**Grant Alpha Access**:
- Web Interface: `/admin` (requires admin authentication)
- Local Script: `python3 grant_alpha_access.py user@email.com`
- Remote API: `python3 manage_render_users.py grant https://app.onrender.com user@email.com`

**Alpha Tester Benefits**:
- 10 profile limit (vs 1 for free users)
- Unlimited annotations (vs 5/hour for free users)
- "Alpha Tester" badge in navigation
- No Stripe subscription required

**Admin Requirements**:
- Must set `ADMIN_EMAILS` environment variable
- Must be logged in as whitelisted admin user
- Optional: `ADMIN_PASSWORD` for additional security layer
