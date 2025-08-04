# 🚀 Deployment Guide - Render Free Tier

This guide walks you through deploying the AI Lesson Plan Annotator to Render's free tier.

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **API Keys**: Have your Llama/OpenAI API key ready

## 🔧 Render Configuration

### Step 1: Create Web Service

1. Go to your [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `ai-lesson-plan-annotator` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

### Step 2: Environment Variables

Add these environment variables in the Render dashboard:

**Required:**
```
LLAMA_API_KEY=your_actual_llama_api_key_here
FLASK_SECRET_KEY=your_secure_random_secret_key_here
FLASK_ENV=production
```

**Optional (for Stripe features):**
```
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_MONTHLY_PRICE_ID=price_your_price_id
```

### Step 3: Database Configuration

The app uses SQLite which will work on Render's free tier. The database file will be created automatically on first run.

**Note**: On Render's free tier, the filesystem is ephemeral, so the database will reset when the service restarts. For production, consider upgrading to a paid plan with persistent disks or using an external database.

## 🌐 Domain & SSL

Render provides:
- **Free subdomain**: `your-app-name.onrender.com`
- **Automatic HTTPS**: SSL certificates are handled automatically
- **Custom domains**: Available on paid plans

## ⚙️ Free Tier Limitations

**Render Free Tier includes:**
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ Automatic HTTPS
- ✅ Global CDN
- ❌ Services spin down after 15 minutes of inactivity
- ❌ 750 hours/month limit
- ❌ No persistent storage

**Important**: Free services "sleep" after 15 minutes of inactivity and take ~30 seconds to wake up.

## 🔄 Deployment Process

1. **Push to GitHub**: Ensure all changes are committed and pushed
2. **Create Service**: Follow Step 1 above
3. **Set Environment Variables**: Add your API keys (Step 2)
4. **Deploy**: Render will automatically build and deploy
5. **Monitor**: Check logs in Render dashboard for any issues

## 📝 Post-Deployment Checklist

- [ ] App loads at your Render URL
- [ ] Landing page displays correctly for anonymous users
- [ ] User registration works
- [ ] User login works
- [ ] PDF upload and processing works (requires valid API key)
- [ ] Profile management functions properly
- [ ] Stripe integration works (if configured)

## 🛠️ Troubleshooting

### Common Issues:

**Build Failures:**
- Check that `requirements.txt` includes all dependencies
- Verify Python version compatibility

**App Won't Start:**
- Check environment variables are set correctly
- Review startup logs in Render dashboard
- Ensure `FLASK_SECRET_KEY` is set

**Database Issues:**
- SQLite database is created automatically
- Database resets on service restart (free tier limitation)

**API Errors:**
- Verify `LLAMA_API_KEY` is valid and has credits
- Check API key format and permissions

### Viewing Logs:
1. Go to your service in Render dashboard
2. Click on **"Logs"** tab
3. Monitor real-time logs for errors

## 🔧 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `LLAMA_API_KEY` | Yes | Your Llama or OpenAI API key |
| `FLASK_SECRET_KEY` | Yes | Secure random string for sessions |
| `FLASK_ENV` | No | Set to 'production' for deployment |
| `STRIPE_PUBLISHABLE_KEY` | No | Stripe public key for payments |
| `STRIPE_SECRET_KEY` | No | Stripe secret key for payments |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook secret |
| `STRIPE_MONTHLY_PRICE_ID` | No | Stripe price ID for $5/month |

## 📈 Upgrading from Free Tier

To upgrade for production use:
- **Paid Plans**: Get persistent storage and no sleep mode
- **External Database**: PostgreSQL add-on for data persistence
- **Custom Domain**: Professional appearance
- **More Resources**: Higher RAM/CPU limits

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-flask)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Custom Domains](https://render.com/docs/custom-domains)

---

**Need Help?** Check the logs in your Render dashboard or refer to the troubleshooting section above.