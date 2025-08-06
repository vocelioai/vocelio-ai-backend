# Simple Railway Environment Upload Script
# Uploads processed environment variables to Railway

param(
    [switch]$DryRun = $false
)

Write-Host "Vocelio Railway Environment Upload" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Gray

# Check Railway CLI
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Railway CLI..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

# Process environment file
Write-Host "Processing environment variables..." -ForegroundColor Yellow
python scripts/process-env-for-railway.py

if (-not (Test-Path ".env.railway.deploy")) {
    Write-Host "Error: Railway deploy file not created" -ForegroundColor Red
    exit 1
}

# Show what will be uploaded
Write-Host "Environment variables ready for upload:" -ForegroundColor Cyan
Get-Content ".env.railway.deploy" | Where-Object { $_ -match "^[^#].*=" } | ForEach-Object {
    $key = ($_ -split "=")[0]
    Write-Host "  $key" -ForegroundColor White
}

if ($DryRun) {
    Write-Host "DRY RUN - Use without -DryRun to actually upload" -ForegroundColor Cyan
} else {
    Write-Host "Authenticating with Railway..." -ForegroundColor Yellow
    railway login
    
    Write-Host "Linking project..." -ForegroundColor Yellow
    railway link
    
    Write-Host "Uploading environment variables..." -ForegroundColor Yellow
    railway variables set --from-env-file .env.railway.deploy
    
    Write-Host "Environment variables uploaded successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to Railway dashboard" -ForegroundColor White
Write-Host "2. Replace placeholder API keys with real values" -ForegroundColor White
Write-Host "3. Deploy with: railway up" -ForegroundColor White
