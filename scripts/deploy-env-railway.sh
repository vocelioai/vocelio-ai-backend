#!/bin/bash

# Railway Environment Deployment Script
# This script automatically uploads .env variables to Railway

echo "🚀 Deploying Environment Variables to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (will open browser if not authenticated)
echo "🔐 Authenticating with Railway..."
railway login

# Link to your Railway project
echo "🔗 Linking to Railway project..."
# You'll need to run: railway link
# Or if you know your project ID: railway link [PROJECT_ID]

# Upload environment variables from .env file
echo "📤 Uploading environment variables..."

# Railway CLI can automatically read from .env file
railway variables set --from-env-file .env

echo "✅ Environment variables successfully deployed to Railway!"
echo "🌐 You can verify them at: https://railway.app/dashboard"
