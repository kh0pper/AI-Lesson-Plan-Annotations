# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered lesson plan annotation web application built with Flask. The app allows teachers to upload PDF lesson plans and receive AI-generated pedagogical insights and recommendations. It features user authentication, custom annotation profiles, Stripe subscription management, secure admin panel, and multiple PDF output formats with persistent PostgreSQL database storage.

## Key Commands

### Development & Testing
```bash
# Setup (first time)
pip install -r requirements.txt
python3 init_db.py

# Run application
python3 app.py                       # Default on port 5001

# Test components
python3 test_auth_system.py          # Authentication
python3 test_profiles.py             # Profile management  
python3 test_webhook.py              # Stripe webhooks
python3 test_gift_card_api.py        # Gift card integration

# Command line annotation
python3 lesson_annotator.py
```

### Database & Admin Management
```bash
# Database setup (PostgreSQL in production, SQLite locally)
python3 init_db.py

# User management
python3 grant_alpha_access.py user@email.com              # Local
python3 manage_render_users.py grant URL user@email.com   # Remote

# Health check
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
- **User**: Authentication, subscriptions, password recovery, access levels (free/premium/alpha)
- **AnnotationProfile**: Custom user annotation preferences stored as JSON
- **FeedbackReport**: Bug reports and feature requests with admin management
- **GiftCard**: Teachers Pay Teachers integration with secure redemption codes
- **UsageRecord**: Rate limiting and analytics tracking
- Auto-detects PostgreSQL (production) vs SQLite (development) via `DATABASE_URL`

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

**Password Recovery System** (`forms.py`, password reset routes in `app.py`):
- PasswordResetRequestForm: Email-based password reset request
- PasswordResetForm: Secure new password setting with confirmation
- Token-based recovery with 1-hour expiration
- Protection against email enumeration attacks
- Ready for email integration (currently shows reset URLs for testing)

### Configuration

**Configuration**:
- **Environment Variables**: `LLAMA_API_KEY`, `DATABASE_URL`, `STRIPE_*`, `ADMIN_EMAILS`, `TPT_API_KEY`
- **Annotation Presets**: Predefined parameters in `annotation_parameters.py`

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

## Critical Implementation Notes

- **Port**: Runs on 5001 (not 5000 as documented in README.md)
- **Database**: PostgreSQL (production) via `DATABASE_URL`, SQLite (development), no migrations
- **Authentication**: Landing page for anonymous users, login required for annotation tools
- **Admin Security**: Multi-layer auth (login + `ADMIN_EMAILS` whitelist + optional password)
- **Stripe Setup**: Requires webhook at `/stripe-webhook` and Customer Portal configuration
- **Rate Limiting**: In-memory storage (not suitable for multi-instance deployment)
- **Processing**: Synchronous PDF processing (consider async for large files)
- **API Keys**: Real `LLAMA_API_KEY` required (demo mode removed)

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

## UI Architecture

**Frontend**: Bootstrap 5 with responsive design, dynamic forms, real-time filtering
**Templates**: Landing page, authentication flow, admin panel, feedback system
**Key Features**: Multi-format PDF upload, profile management, subscription billing portal

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
- `GET/POST /reset-password` - Password reset request form
- `GET/POST /reset-password/<token>` - Password reset completion with token

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

## Production Status

**PRODUCTION READY** - Complete lesson plan annotation system with:
- User lifecycle management (registration, authentication, password recovery)
- Stripe subscription system with billing portal
- Teachers Pay Teachers gift card integration (tested and operational)
- Multi-format PDF annotation pipeline with AI integration
- Comprehensive admin panel with feedback management
- Rate limiting and usage analytics