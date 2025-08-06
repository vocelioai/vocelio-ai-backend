# 🚀 Auto-Load .env to Railway - Quick Guide

Your Vocelio backend now includes **3 automated methods** to upload environment variables to Railway without manual copying!

## 🎯 Quick Start (Recommended)

### Method 1: One-Command Upload
```powershell
# Process and upload in one command
.\scripts\railway-upload-simple.ps1

# Test first (dry run)
.\scripts\railway-upload-simple.ps1 -DryRun
```

### Method 2: Manual Railway CLI
```bash
# 1. Login to Railway
railway login

# 2. Link your project
railway link

# 3. Auto-upload from processed .env file
railway variables set --from-env-file .env.railway.deploy
```

### Method 3: Cross-Platform Script
```bash
# On Linux/Mac
./scripts/deploy-env-railway.sh

# On Windows
.\scripts\deploy-env-railway.ps1
```

## 🔧 What Happens Automatically

1. **🔒 Security First**: Real API keys are replaced with placeholders
2. **🏗️ Railway Optimization**: Database/Redis URLs use Railway's environment variables
3. **📦 Production Ready**: Environment switches to production mode
4. **⚡ Batch Upload**: All 80+ variables uploaded at once

## 📋 Processed Variables

The script automatically handles:
- ✅ **Database**: Uses Railway's PostgreSQL variables
- ✅ **Redis**: Uses Railway's Redis URL
- ✅ **API Keys**: Replaced with secure placeholders
- ✅ **Service Ports**: All 25 microservice configurations
- ✅ **CORS**: Updated for production domains
- ✅ **Environment**: Set to production mode

## 🔑 After Upload - Add Real API Keys

In your Railway dashboard, replace these placeholders:
```
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
```

## 🚀 Deploy Your Services

After environment variables are set:
```bash
# Deploy all services
railway up

# Or deploy specific service
railway up --service ai-brain
```

## 📁 Generated Files

- `📄 .env.railway.deploy` - Processed environment file
- `📖 RAILWAY_ENV_UPLOAD.md` - Detailed instructions
- `🔧 scripts/railway-upload-simple.ps1` - Upload script

## 🔗 Quick Links

- **Railway Dashboard**: https://railway.app/dashboard
- **GitHub Repository**: https://github.com/vocelioai/vocelio-ai-backend
- **Environment Templates**: `.env.example`, `.env.railway`

---

**🎉 No more manual copying of 80+ environment variables!**
