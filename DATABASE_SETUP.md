# Database Setup for Persistent Storage

## Problem

The application was using SQLite with local file storage, which is **ephemeral** on cloud platforms like Render. This means:
- ❌ User registrations get lost on app restarts/deployments
- ❌ Data is not persistent between deployments
- ❌ Database resets every time the app redeploys

## Solution

Updated to use **PostgreSQL** for persistent storage with automatic fallback to SQLite for local development.

## Render Database Setup

### Option 1: Render PostgreSQL (Recommended)
1. **Create PostgreSQL Database**:
   - Go to Render Dashboard
   - Click "New +" → "PostgreSQL"
   - Name: `ai-lesson-annotator-db`
   - User: `ai_annotator`
   - Database: `ai_annotator_production`
   - Plan: **Free** (suitable for development/small apps)

2. **Get Database URL**:
   - After creation, copy the **External Database URL**
   - Should look like: `postgresql://user:password@hostname:port/database`

3. **Configure Environment Variable**:
   - Go to your Web Service → Environment
   - Add: `DATABASE_URL=postgresql://user:password@hostname:port/database`

### Option 2: External PostgreSQL
You can also use external providers:
- **Neon** (Free tier available)
- **Supabase** (Free tier available) 
- **Railway** (Free tier available)
- **ElephantSQL** (Free tier available)

## Environment Variables

### Required for Persistent Database
```bash
# PostgreSQL database URL (from Render or external provider)
DATABASE_URL=postgresql://user:password@hostname:port/database
```

### Complete Environment Setup
```bash
# Database
DATABASE_URL=postgresql://user:password@hostname:port/database

# Admin Configuration  
ADMIN_EMAILS=your-email@domain.com
ADMIN_API_KEY=your-secure-admin-key-2024

# Optional Admin Security
ADMIN_PASSWORD=YourSecurePassword123!
ADMIN_IP_WHITELIST=your.ip.address.here

# Flask Configuration
FLASK_SECRET_KEY=your-flask-secret-key-here

# Stripe Configuration (your existing keys)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_MONTHLY_PRICE_ID=price_...

# LLM API Key
LLM_API_KEY=LLM|2844169445921515|41boeUYoeZ-6wV99tSi8KzABTJE
```

## Database Features

### ✅ Automatic Database Detection
- **Production**: Uses `DATABASE_URL` (PostgreSQL)
- **Development**: Falls back to SQLite (`ai_annotator.db`)
- **Logging**: Shows which database is being used

### ✅ Robust Error Handling  
- Database connection errors are caught and logged
- User registration has improved error handling
- Prevents duplicate users (email/username)
- Transaction rollback on errors

### ✅ Automatic Table Creation
- Tables are created automatically on first run
- No manual database schema setup required
- Works for both PostgreSQL and SQLite

## Verification Steps

1. **Check Logs**: Look for database initialization messages:
   ```
   🗄️ Database URL: postgresql://user:password@hostname...
   ✅ Database tables created successfully
   ```

2. **Test Registration**: Try registering a new user
   ```
   ✅ New user registered: testuser (test@domain.com)
   ```

3. **Test Persistence**: 
   - Register a user
   - Trigger a deployment (push to GitHub)
   - Verify user still exists after deployment

## Troubleshooting

### "Database initialization error"
- Check `DATABASE_URL` format
- Ensure PostgreSQL service is running
- Verify database credentials

### "Username or email already exists"
- User data is now persistent
- Previous test registrations may still exist
- Use different email/username

### Database Connection Issues
- Verify `DATABASE_URL` is correctly set
- Check PostgreSQL service status on Render
- Ensure database allows external connections

## Migration from SQLite

If you had test data in SQLite that you want to preserve:
1. The new system will start fresh with PostgreSQL
2. Previous SQLite data was ephemeral anyway
3. Admin users will need to re-register accounts
4. Set up admin email whitelist in environment variables

## Cost Considerations

- **Render PostgreSQL Free Tier**: 
  - 1GB storage
  - 1 month retention
  - Suitable for development/small apps

- **Paid Tiers**: Available if you need more storage/retention

## Next Steps After Setup

1. **Configure** `DATABASE_URL` in Render environment
2. **Deploy** the updated application  
3. **Test** user registration persistence
4. **Set up** admin email whitelist
5. **Register** your admin account
6. **Grant** alpha access to users

The database will now persist data across deployments and restarts!