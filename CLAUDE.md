# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

### Database Management
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

*User Model:*
- Authentication: username, email, password_hash with bcrypt
- Subscription: subscription_status, stripe_customer_id, access_type, expires_at
- Limits: profile_limit (1 for free, 10 for premium/alpha)
- Methods: is_premium(), is_alpha_tester(), get_access_type(), check_password()

*AnnotationProfile Model:*
- Custom user annotation preferences with JSON storage
- Fields: name, description, is_default, pedagogical_approach, engagement_level
- Advanced options: assessment_type, differentiation, language_focus, age_group
- Visual: annotation_theme, custom_category_definitions
- Relationships: ForeignKey to User with cascade delete

*FeedbackReport Model:*
- Comprehensive feedback tracking system
- Core: report_type (bug/feature_request/improvement/other), title, description
- Management: priority (low/medium/high/critical), status (open/in_progress/resolved/closed)
- Technical: browser_info, error_details, steps_to_reproduce
- Admin: admin_notes, resolved_at timestamps
- Methods: get_type_badge(), get_priority_badge(), get_status_badge() for UI
- Relationships: ForeignKey to User with cascade delete

*UsageRecord Model:*
- Rate limiting and usage analytics tracking

*GiftCard Model:*
- Teachers Pay Teachers integration for premium access gift cards
- Secure code generation with XXXX-XXXX-XXXX format using cryptographic randomness
- Purchase tracking: purchase_source, purchase_id, purchase_email, purchase_date
- Redemption tracking: redeemed_by_user_id, redeemed_at, redeemed_ip
- Validation: is_valid() method checks redemption status and expiration
- Auto-granting: redeem() method automatically extends user premium access
- Admin methods: to_dict(), get_status_badge() for UI display
- Relationships: ForeignKey to User with redemption history

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
- Tabbed interface: User Management + Feedback Management
- Complete user lifecycle management: create, password reset, delete accounts
- User management interface with search/filtering and quick action buttons
- Alpha tester management system with API endpoints
- Feedback and bug report management with status tracking
- Admin action logging with IP tracking and safety confirmations
- Web interface accessible at `/admin` for authorized users only

**Feedback System** (`forms.py`, feedback routes in `app.py`):
- User feedback submission with categorization (bugs, features, improvements, other)
- Dynamic form sections based on report type (technical details for bugs)
- Priority levels (low, medium, high, critical) and status tracking
- Admin management interface integrated in admin panel with tabbed UI
- User feedback history at `/my-feedback` with visual status indicators
- Real-time filtering and search capabilities in admin interface
- Browser information capture for debugging purposes
- Comprehensive admin notes system for feedback resolution tracking

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
- `TPT_API_KEY` - API key for Teachers Pay Teachers gift card integration

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

## Template Structure

**Base Template** (`templates/base.html`):
- Bootstrap 5 responsive design with Font Awesome icons
- Navigation includes authenticated user menu with access badges
- Feedback link in main navigation for logged-in users
- User dropdown with "My Feedback" access and billing management
- Copyright updated to 2025

**Main Pages**:
- `templates/index.html` - Primary upload interface with comprehensive form options
- `templates/landing.html` - Marketing page for anonymous users
- `templates/feedback.html` - Feedback submission form with dynamic sections
- `templates/my_feedback.html` - User feedback history with status cards
- `templates/admin.html` - Tabbed admin interface (User Management + Feedback)

**Key UI Features**:
- Responsive card-based design with hover effects
- Dynamic form sections that show/hide based on selections
- Visual status badges for feedback reports and user access levels
- Bootstrap modal dialogs for admin actions
- Real-time search and filtering without page refresh
- Professional styling with consistent color schemes

## API Endpoints

**Public Routes**:
- `GET /` - Landing page for anonymous users, upload interface for authenticated
- `POST /upload` - PDF upload and annotation processing (login required)
- `GET /feedback` - Feedback submission form (login required)
- `POST /feedback` - Process feedback submission (login required)
- `GET /my-feedback` - User's feedback history (login required)

**Authentication Routes**:
- `GET/POST /login` - User authentication
- `GET/POST /register` - User registration
- `GET /logout` - User logout

**Subscription Routes**:
- `GET /donate` - Stripe subscription page
- `POST /create-checkout-session` - Stripe checkout session creation
- `POST /stripe-webhook` - Stripe webhook endpoint for subscription events
- `GET /billing-portal` - Stripe billing portal redirect (premium users)

**Gift Card Routes**:
- `GET /gift-cards/redeem` - Gift card redemption page (login required)
- `POST /gift-cards/redeem` - Process gift card redemption (login required)
- `POST /api/gift-cards/validate` - Validate gift card without redeeming (public)
- `POST /api/gift-cards/generate` - Generate gift card for Teachers Pay Teachers (API key required)

**Admin API Endpoints** (requires admin authentication):
- `GET /admin` - Admin panel web interface
- `GET /admin/list-users` - List all users with filtering
- `POST /admin/grant-access` - Grant alpha/premium access to users
- `POST /admin/revoke-access` - Revoke special access from users
- `POST /admin/create-user` - Create new user accounts with access level assignment
- `POST /admin/update-password` - Reset/update passwords for any user account
- `POST /admin/delete-user` - Delete user accounts with cascade cleanup
- `GET /admin/feedback` - List all feedback reports with filtering
- `POST /admin/feedback/<id>` - Update feedback status and admin notes
- `GET /admin/gift-cards` - List all gift cards with status filtering
- `POST /admin/gift-cards/generate` - Generate gift cards manually
- `POST /admin/logout` - Admin logout

## Recent Updates Summary

The application has been significantly enhanced with:

1. **Complete User Account Management**: Admins can now create new user accounts, reset passwords, and delete accounts through the admin panel with comprehensive validation, safety confirmations, and audit logging.

2. **Comprehensive Feedback System**: Users can submit bug reports, feature requests, and improvement suggestions through a dedicated form with dynamic fields, priority levels, and technical details capture.

3. **Enhanced Admin Panel**: Multi-tabbed interface combining user management and feedback management with real-time filtering, search capabilities, quick action buttons, and comprehensive admin tools.

4. **Improved User Experience**: Updated navigation with feedback links, visual status indicators, responsive design improvements, and intuitive card-based interfaces throughout the application.

5. **Database Architecture**: Added FeedbackReport model with full relationship mapping and cascade delete functionality for data integrity.

6. **Security & Authentication**: Multi-layer admin authentication, comprehensive input validation, admin action logging, and protection against accidental admin user deletion.

7. **Gift Card System**: Complete Teachers Pay Teachers integration with secure gift card generation, redemption workflow, admin management, and automatic premium access granting for monetization through educational marketplaces.

The codebase now represents a mature, production-ready lesson plan annotation system with complete user lifecycle management, feedback collection, comprehensive administrative capabilities, and integrated gift card monetization through Teachers Pay Teachers.