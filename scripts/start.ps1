# Vocelio Backend Startup Script for Windows
Write-Host "🚀 Starting Vocelio Backend Services..." -ForegroundColor Green

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to start a service
function Start-Service {
    param(
        [string]$ServiceName,
        [int]$Port,
        [string]$AppPath
    )
    
    Write-Host "🔧 Starting $ServiceName on port $Port..." -ForegroundColor Blue
    
    if (Test-Port -Port $Port) {
        Write-Host "❌ Port $Port is already in use" -ForegroundColor Red
        return $false
    }
    
    # Change to service directory
    $originalLocation = Get-Location
    Set-Location $AppPath
    
    # Install dependencies if requirements.txt exists
    if (Test-Path "requirements.txt") {
        Write-Host "📦 Installing dependencies for $ServiceName..." -ForegroundColor Yellow
        pip install -r requirements.txt | Out-Null
    }
    
    # Start the service
    $process = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", $Port, "--reload" -PassThru -WindowStyle Hidden
    
    if ($process) {
        Write-Host "✅ $ServiceName started (PID: $($process.Id))" -ForegroundColor Green
        
        # Save PID to file
        if (!(Test-Path "../../pids")) {
            New-Item -ItemType Directory -Path "../../pids" -Force | Out-Null
        }
        $process.Id | Out-File -FilePath "../../pids/$ServiceName.pid" -Encoding ascii
        
        Set-Location $originalLocation
        return $true
    } else {
        Write-Host "❌ Failed to start $ServiceName" -ForegroundColor Red
        Set-Location $originalLocation
        return $false
    }
}

# Create directories for logs and PIDs
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" -Force | Out-Null }
if (!(Test-Path "pids")) { New-Item -ItemType Directory -Path "pids" -Force | Out-Null }

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Blue

try {
    python --version | Out-Null
    Write-Host "✅ Python is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

try {
    pip --version | Out-Null
    Write-Host "✅ pip is available" -ForegroundColor Green
} catch {
    Write-Host "❌ pip is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your configuration" -ForegroundColor Yellow
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Blue

# Start API Gateway first
if (Start-Service -ServiceName "API Gateway" -Port 8000 -AppPath "apps/api-gateway") {
    Start-Sleep -Seconds 2
    
    # Start core services
    Start-Service -ServiceName "Overview Service" -Port 8001 -AppPath "apps/overview" | Out-Null
    Start-Service -ServiceName "Agents Service" -Port 8002 -AppPath "apps/agents" | Out-Null
    Start-Service -ServiceName "Smart Campaigns Service" -Port 8003 -AppPath "apps/smart-campaigns" | Out-Null
    Start-Service -ServiceName "Call Center Service" -Port 8004 -AppPath "apps/call-center" | Out-Null
    Start-Service -ServiceName "Phone Numbers Service" -Port 8005 -AppPath "apps/phone-numbers" | Out-Null
    Start-Service -ServiceName "Voice Marketplace Service" -Port 8006 -AppPath "apps/voice-marketplace" | Out-Null
    Start-Service -ServiceName "Analytics Pro Service" -Port 8007 -AppPath "apps/analytics-pro" | Out-Null
    Start-Service -ServiceName "AI Brain Service" -Port 8008 -AppPath "apps/ai-brain" | Out-Null
    Start-Service -ServiceName "Flow Builder Service" -Port 8009 -AppPath "apps/flow-builder" | Out-Null
    Start-Service -ServiceName "Integrations Service" -Port 8010 -AppPath "apps/integrations" | Out-Null
}

Write-Host ""
Write-Host "🎉 Vocelio Backend Services Started Successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor Blue
Write-Host "  • API Gateway:     http://localhost:8000" -ForegroundColor Green
Write-Host "  • API Docs:        http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  • Overview Service: http://localhost:8001" -ForegroundColor Green
Write-Host "  • Agents Service:  http://localhost:8002" -ForegroundColor Green
Write-Host "  • Smart Campaigns: http://localhost:8003" -ForegroundColor Green
Write-Host "  • Call Center:     http://localhost:8004" -ForegroundColor Green
Write-Host "  • Phone Numbers:   http://localhost:8005" -ForegroundColor Green
Write-Host "  • Voice Marketplace: http://localhost:8006" -ForegroundColor Green
Write-Host "  • Analytics Pro:   http://localhost:8007" -ForegroundColor Green
Write-Host "  • AI Brain:        http://localhost:8008" -ForegroundColor Green
Write-Host "  • Flow Builder:    http://localhost:8009" -ForegroundColor Green
Write-Host "  • Integrations:    http://localhost:8010" -ForegroundColor Green
Write-Host ""
Write-Host "🔍 Health Checks:" -ForegroundColor Blue
Write-Host "  • Gateway Health:  http://localhost:8000/health" -ForegroundColor Green
Write-Host "  • All Services:    http://localhost:8000/services" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Logs are available in the 'logs/' directory" -ForegroundColor Yellow
Write-Host "🛑 To stop services, run: .\scripts\stop.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "✨ Happy coding with Vocelio! ✨" -ForegroundColor Green
