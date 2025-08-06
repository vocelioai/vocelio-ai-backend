# Railway Deployment Script for Vocelio AI Call Center (PowerShell)
# For Windows users

Write-Host "🚀 Deploying Vocelio AI Call Center to Railway..." -ForegroundColor Green

# Check if Railway CLI is installed
try {
    railway --version | Out-Null
    Write-Host "✅ Railway CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ Railway CLI not found. Please install from: https://railway.app/cli" -ForegroundColor Red
    Write-Host "📥 Installation command: iwr https://railway.app/install.ps1 | iex" -ForegroundColor Yellow
    exit 1
}

# Login to Railway
Write-Host "🔐 Logging into Railway..." -ForegroundColor Yellow
railway login

# Create and link project
Write-Host "📁 Setting up Railway project..." -ForegroundColor Yellow
railway project new vocelio-ai-backend

# Add required services
Write-Host "🗄️ Adding database services..." -ForegroundColor Yellow
railway add postgresql
railway add redis

# Set core environment variables
Write-Host "⚙️ Setting environment variables..." -ForegroundColor Yellow
railway variables set PYTHON_VERSION=3.11
railway variables set PORT=8000
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false

# Deploy the application
Write-Host "🚀 Deploying application..." -ForegroundColor Green
railway up

Write-Host "✅ Deployment initiated successfully!" -ForegroundColor Green
Write-Host "🌐 Your API will be available at your Railway domain" -ForegroundColor Cyan

# Display next steps
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to Railway dashboard and set remaining environment variables" -ForegroundColor White
Write-Host "2. Configure your Supabase URL and API keys" -ForegroundColor White
Write-Host "3. Set up Twilio, OpenAI, and other API credentials" -ForegroundColor White
Write-Host "4. Test your API endpoints" -ForegroundColor White
Write-Host "5. Deploy your React dashboard to Vercel/Netlify" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Railway Dashboard: https://railway.app/dashboard" -ForegroundColor Cyan
