# 🚀 AI Lesson Plan Annotator - Setup Instructions

## Quick Start Guide

The application requires several Python packages to run. Follow these steps to get started:

### 1. Install Dependencies

**Option A: Install all at once**
```bash
pip install -r requirements.txt
```

**Option B: Install individually**
```bash
pip install flask flask-login flask-sqlalchemy flask-wtf stripe bcrypt
pip install openai PyPDF2 reportlab pymupdf numpy pillow python-dotenv
```

**Option C: Use virtual environment (recommended)**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

**Create .env file:**
```bash
cp env_example.txt .env
```

**Edit .env with your API keys:**
```bash
# Required for AI functionality
OPENAI_API_KEY=your_openai_api_key_here

# Required for donations (optional for basic use)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_MONTHLY_PRICE_ID=price_...

# Optional
FLASK_SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database

```bash
python3 init_db.py
```

### 4. Start the Application

```bash
python3 app.py
```

**Or use the setup script:**
```bash
python3 setup_and_run.py
```

### 5. Access the Application

Open your browser and go to:
**http://localhost:5000**

---

## 🌟 Features Available

### Free Tier
- ✅ 1 custom annotation profile
- ✅ 5 annotations per hour
- ✅ All PDF formats (Smart Overlay, Inline, Traditional)
- ✅ Custom color themes
- ✅ User accounts and profile saving

### Premium Tier ($5/month donation)
- ⭐ Up to 10 custom annotation profiles
- ⭐ Unlimited annotations (no rate limits)
- ⭐ Priority processing
- ⭐ Billing management portal
- ⭐ Early access to new features

---

## 🔧 Troubleshooting

### "localhost refused to connect"
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Check that the Flask app is running: `python3 app.py`
- Verify the correct port: http://localhost:5000

### "Module not found" errors
- Install missing dependencies: `pip install [package_name]`
- Use virtual environment to avoid conflicts
- Check Python version (3.8+ required)

### Database errors
- Initialize database: `python3 init_db.py`
- Delete ai_annotator.db and reinitialize if corrupted

### Stripe/Payment errors
- Stripe keys are optional for basic functionality
- Get test keys from: https://dashboard.stripe.com/test/apikeys
- Set up webhooks for subscription management

---

## 📁 Project Structure

```
ai-lesson-plan-annotate/
├── app.py                 # Main Flask application
├── models.py             # Database models (User, Profile, Usage)
├── stripe_integration.py # Payment processing
├── lesson_annotator.py   # Core annotation logic
├── requirements.txt      # Python dependencies
├── init_db.py           # Database setup
├── setup_and_run.py     # Automated setup script
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profiles.html
│   └── donate.html
└── static/             # CSS, JS, images
```

---

## 🎯 Next Steps

1. **Get OpenAI API Key**: https://platform.openai.com/api-keys
2. **Set up Stripe Account**: https://dashboard.stripe.com (optional)
3. **Create $5/month product** in Stripe Dashboard
4. **Configure webhook endpoint** at `/stripe-webhook`
5. **Test the application** with sample PDFs

---

## 📞 Support

If you encounter issues:
1. Check this setup guide
2. Review error messages in terminal
3. Ensure all dependencies are installed
4. Verify environment variables are set

The application is designed to work even without Stripe integration - you can use all basic features with just the OpenAI API key configured.

---

## 🚀 Deployment Options

- **Local Development**: Follow this guide
- **Heroku**: Use Procfile and Heroku Postgres
- **DigitalOcean**: Use App Platform with environment variables
- **Railway**: Direct GitHub deployment
- **PythonAnywhere**: Flask-friendly hosting
- **AWS/GCP**: Use container services or App Engine