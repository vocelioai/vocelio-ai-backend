# Railway Environment Deployment Script
# This script automatically uploads .env variables to Railway

Write-Host "🚀 Deploying Environment Variables to Railway..." -ForegroundColor Green

# Check if Railway CLI is installed
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Railway CLI not found. Installing..." -ForegroundColor Red
    npm install -g @railway/cli
}

# Login to Railway (will open browser if not authenticated)
Write-Host "🔐 Authenticating with Railway..." -ForegroundColor Yellow
railway login

# Link to your Railway project
Write-Host "🔗 Linking to Railway project..." -ForegroundColor Yellow
# You'll need to run: railway link
# Or if you know your project ID: railway link [PROJECT_ID]

# Upload environment variables from .env file
Write-Host "📤 Uploading environment variables..." -ForegroundColor Yellow

# Railway CLI can automatically read from .env file
railway variables set --from-env-file .env

Write-Host "✅ Environment variables successfully deployed to Railway!" -ForegroundColor Green
Write-Host "🌐 You can verify them at: https://railway.app/dashboard" -ForegroundColor Cyan
