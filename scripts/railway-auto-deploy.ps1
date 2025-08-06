# Vocelio Railway Auto-Deploy Script
# Automatically processes and uploads environment variables to Railway

param(
    [string]$ProjectId = "",
    [switch]$DryRun = $false
)

Write-Host "🚀 Vocelio Railway Auto-Deploy Started" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray

# Check if Railway CLI is installed
Write-Host "Checking Railway CLI..." -ForegroundColor Yellow
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Railway CLI..." -ForegroundColor Yellow
    npm install -g @railway/cli
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install Railway CLI" -ForegroundColor Red
        exit 1
    }
    Write-Host "Railway CLI installed successfully" -ForegroundColor Green
} else {
    Write-Host "Railway CLI found" -ForegroundColor Green
}

# Process environment file for Railway
Write-Host "🔄 Processing environment variables..." -ForegroundColor Yellow
python scripts/process-env-for-railway.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to process environment file" -ForegroundColor Red
    exit 1
}

# Check if .env.railway.deploy was created
if (-not (Test-Path ".env.railway.deploy")) {
    Write-Host "❌ Railway deploy file not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Environment file processed successfully" -ForegroundColor Green

# Authenticate with Railway
Write-Host "🔐 Authenticating with Railway..." -ForegroundColor Yellow
Write-Host "   (This will open your browser if not already authenticated)" -ForegroundColor Gray

if (-not $DryRun) {
    railway login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Railway authentication failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Railway authentication successful" -ForegroundColor Green
}

# Link to Railway project
Write-Host "🔗 Linking to Railway project..." -ForegroundColor Yellow

if ($ProjectId) {
    Write-Host "   Using Project ID: $ProjectId" -ForegroundColor Gray
    if (-not $DryRun) {
        railway link $ProjectId
    }
} else {
    Write-Host "   Interactive project selection" -ForegroundColor Gray
    if (-not $DryRun) {
        railway link
    }
}

if (-not $DryRun -and $LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to link Railway project" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Railway project linked" -ForegroundColor Green

# Upload environment variables
Write-Host "📤 Uploading environment variables..." -ForegroundColor Yellow
Write-Host "   Source: .env.railway.deploy" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "🧪 DRY RUN - Would execute: railway variables set --from-env-file .env.railway.deploy" -ForegroundColor Cyan
    
    # Show what would be uploaded
    Write-Host "📋 Environment variables that would be uploaded:" -ForegroundColor Cyan
    Get-Content ".env.railway.deploy" | Where-Object { $_ -match "^[^#].*=" } | ForEach-Object {
        $key = ($_ -split "=")[0]
        Write-Host "   • $key" -ForegroundColor White
    }
} else {
    railway variables set --from-env-file .env.railway.deploy
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to upload environment variables" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Environment variables uploaded successfully" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "🎉 Deployment Summary" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host "✅ Environment file processed" -ForegroundColor Green
Write-Host "✅ Railway CLI authenticated" -ForegroundColor Green
Write-Host "✅ Project linked" -ForegroundColor Green
if ($DryRun) {
    Write-Host "🧪 Environment variables ready for upload (DRY RUN)" -ForegroundColor Cyan
} else {
    Write-Host "✅ Environment variables uploaded" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔄 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to your Railway dashboard: https://railway.app/dashboard" -ForegroundColor White
Write-Host "2. Add your real API keys (replace placeholder values)" -ForegroundColor White
Write-Host "3. Deploy your services with: railway up" -ForegroundColor White

Write-Host ""
Write-Host "📖 For manual variable management, see: RAILWAY_ENV_UPLOAD.md" -ForegroundColor Gray

# Cleanup
if (Test-Path ".env.railway.deploy") {
    Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Gray
    # Remove-Item ".env.railway.deploy" -Force
    Write-Host "   Keeping .env.railway.deploy for reference" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🚀 Vocelio Railway Auto-Deploy Complete!" -ForegroundColor Green
