#!/usr/bin/env pwsh

# 🚀 Railway Deployment Script - All Services
# Deploy remaining 23 services (API Gateway already deployed)

Write-Host "🚀 Deploying Remaining 23 Services" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Service list (excluding api-gateway which is already deployed)
$services = @(
    "agents:apps/agents:8002",
    "ai-brain:apps/ai-brain:8003",
    "call-center:apps/call-center:8004",
    "integrations:apps/integrations:8005",
    "knowledge-base:apps/knowledge-base:8006",
    "voice-lab:apps/voice-lab:8007",
    "notifications:apps/notifications:8009",
    "phone-numbers:apps/phone-numbers:8010",
    "analytics-pro:apps/analytics-pro:8011",
    "team-hub:apps/team-hub:8012",
    "webhooks:apps/webhooks:8013",
    "lead-management:apps/lead-management:8014",
    "scheduling:apps/scheduling:8016",
    "smart-campaigns:apps/smart-campaigns:8018",
    "billing-pro:apps/billing-pro:8019",
    "compliance:apps/compliance:8020",
    "flow-builder:apps/flow-builder:8021",
    "voice-marketplace:apps/voice-marketplace:8024",
    "developer-api:apps/developer-api:8008",
    "agent-store:apps/agent-store:8023",
    "scripts:apps/scripts:8015",
    "settings:apps/settings:8017",
    "white-label:apps/white-label:8022"
)

$deployCount = 0
$totalServices = $services.Count

foreach ($serviceConfig in $services) {
    $parts = $serviceConfig.Split(":")
    $serviceName = $parts[0]
    $serviceDir = $parts[1]
    $servicePort = $parts[2]
    
    $deployCount++
    Write-Host ""
    Write-Host "📦 Deploying $serviceName ($deployCount/$totalServices)" -ForegroundColor Green
    Write-Host "   Directory: $serviceDir" -ForegroundColor Gray
    Write-Host "   Port: $servicePort" -ForegroundColor Gray
    
    # Navigate to service directory
    Set-Location $serviceDir
    
    # Set environment variables
    Write-Host "   Setting environment variables..." -ForegroundColor Yellow
    & railway variables --set "PORT=$servicePort" --set "PYTHONPATH=/app" --set "ENVIRONMENT=production" --set "RAILWAY_RUN_COMMAND=python railway_start.py"
    
    # Deploy the service
    Write-Host "   Deploying to Railway..." -ForegroundColor Yellow
    & railway up --detach
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $serviceName deployed!" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to deploy $serviceName" -ForegroundColor Red
    }
    
    # Return to root
    Set-Location "../.."
    
    # Brief pause
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "Deployed $deployCount additional services" -ForegroundColor White
Write-Host "Total: 25/25 services (including Overview + API Gateway)" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 Check Railway Dashboard: https://railway.app/dashboard" -ForegroundColor Blue
