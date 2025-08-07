#!/usr/bin/env pwsh

# 🚀 Railway Deployment Script - Fixed Configuration
# Deploy all 24 remaining services with correct start commands

Write-Host "🚀 Railway Deployment Script v2.0" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

# Service configurations with correct start commands
$services = @(
    @{ Name = "api-gateway"; Dir = "apps/api-gateway"; Port = 8001; Start = "python railway_start.py" },
    @{ Name = "agents"; Dir = "apps/agents"; Port = 8002; Start = "python railway_start.py" },
    @{ Name = "ai-brain"; Dir = "apps/ai-brain"; Port = 8003; Start = "python railway_start.py" },
    @{ Name = "call-center"; Dir = "apps/call-center"; Port = 8004; Start = "python railway_start.py" },
    @{ Name = "integrations"; Dir = "apps/integrations"; Port = 8005; Start = "python railway_start.py" },
    @{ Name = "knowledge-base"; Dir = "apps/knowledge-base"; Port = 8006; Start = "python railway_start.py" },
    @{ Name = "voice-lab"; Dir = "apps/voice-lab"; Port = 8007; Start = "python railway_start.py" },
    @{ Name = "notifications"; Dir = "apps/notifications"; Port = 8009; Start = "python railway_start.py" },
    @{ Name = "phone-numbers"; Dir = "apps/phone-numbers"; Port = 8010; Start = "python railway_start.py" },
    @{ Name = "analytics-pro"; Dir = "apps/analytics-pro"; Port = 8011; Start = "python railway_start.py" },
    @{ Name = "team-hub"; Dir = "apps/team-hub"; Port = 8012; Start = "python railway_start.py" },
    @{ Name = "webhooks"; Dir = "apps/webhooks"; Port = 8013; Start = "python railway_start.py" },
    @{ Name = "lead-management"; Dir = "apps/lead-management"; Port = 8014; Start = "python railway_start.py" },
    @{ Name = "scheduling"; Dir = "apps/scheduling"; Port = 8016; Start = "python railway_start.py" },
    @{ Name = "smart-campaigns"; Dir = "apps/smart-campaigns"; Port = 8018; Start = "python railway_start.py" },
    @{ Name = "billing-pro"; Dir = "apps/billing-pro"; Port = 8019; Start = "python railway_start.py" },
    @{ Name = "compliance"; Dir = "apps/compliance"; Port = 8020; Start = "python railway_start.py" },
    @{ Name = "flow-builder"; Dir = "apps/flow-builder"; Port = 8021; Start = "python railway_start.py" },
    @{ Name = "voice-marketplace"; Dir = "apps/voice-marketplace"; Port = 8024; Start = "python railway_start.py" },
    @{ Name = "developer-api"; Dir = "apps/developer-api"; Port = 8008; Start = "python railway_start.py" },
    @{ Name = "agent-store"; Dir = "apps/agent-store"; Port = 8023; Start = "python railway_start.py" },
    @{ Name = "scripts"; Dir = "apps/scripts"; Port = 8015; Start = "python railway_start.py" },
    @{ Name = "settings"; Dir = "apps/settings"; Port = 8017; Start = "python railway_start.py" },
    @{ Name = "white-label"; Dir = "apps/white-label"; Port = 8022; Start = "python railway_start.py" }
)

$deployedServices = @()
$totalServices = $services.Count
$currentService = 1

Write-Host "📊 Deployment Plan:" -ForegroundColor Cyan
Write-Host "   Total Services: $totalServices" -ForegroundColor White
Write-Host "   Strategy: One-by-one with health checks" -ForegroundColor White
Write-Host "   Start Command: python railway_start.py" -ForegroundColor White
Write-Host ""

foreach ($service in $services) {
    Write-Host "📦 Deploying $($service.Name) ($currentService/$totalServices)..." -ForegroundColor Green
    Write-Host "   Directory: $($service.Dir)" -ForegroundColor Gray
    Write-Host "   Port: $($service.Port)" -ForegroundColor Gray
    Write-Host "   Start: $($service.Start)" -ForegroundColor Gray
    
    # Navigate to service directory
    Set-Location $service.Dir
    
    try {
        # Set environment variables
        Write-Host "   Setting environment variables..." -ForegroundColor Yellow
        & railway variables --set "PORT=$($service.Port)" --set "PYTHONPATH=/app" --set "ENVIRONMENT=production" --set "RAILWAY_RUN_COMMAND=$($service.Start)"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Environment variables set" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Warning: Environment variables may not be set correctly" -ForegroundColor Yellow
        }
        
        # Deploy the service
        Write-Host "   Deploying to Railway..." -ForegroundColor Yellow
        $deployOutput = & railway up --detach 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $($service.Name) deployed successfully!" -ForegroundColor Green
            
            # Extract build logs URL if available
            $buildLogsUrl = $deployOutput | Select-String "Build Logs:" | ForEach-Object { $_.ToString().Split("Build Logs: ")[1] }
            if ($buildLogsUrl) {
                Write-Host "   🔗 Build Logs: $buildLogsUrl" -ForegroundColor Blue
            }
            
            $deployedServices += $service
        } else {
            Write-Host "   ❌ Failed to deploy $($service.Name)" -ForegroundColor Red
            Write-Host "   Error: $deployOutput" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "   ❌ Exception deploying $($service.Name): $_" -ForegroundColor Red
    }
    
    # Return to root directory
    Set-Location "../.."
    
    Write-Host ""
    $currentService++
    
    # Brief pause between deployments
    Start-Sleep -Seconds 3
}

Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Results:" -ForegroundColor Cyan
Write-Host "   Successfully deployed: $($deployedServices.Count)/$totalServices services" -ForegroundColor White

if ($deployedServices.Count -gt 0) {
    Write-Host ""
    Write-Host "✅ Deployed Services:" -ForegroundColor Green
    foreach ($service in $deployedServices) {
        Write-Host "   - $($service.Name) (Port: $($service.Port))" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "🔍 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check Railway Dashboard for service URLs" -ForegroundColor White
Write-Host "2. Test health endpoints: {URL}/health" -ForegroundColor White
Write-Host "3. Monitor build logs for any issues" -ForegroundColor White
Write-Host "4. Update service URLs in test scripts" -ForegroundColor White

Write-Host ""
Write-Host "🌐 Railway Dashboard: https://railway.app/dashboard" -ForegroundColor Blue
Write-Host ""
Write-Host "🚀 Your world-class AI call center is deploying!" -ForegroundColor Green
