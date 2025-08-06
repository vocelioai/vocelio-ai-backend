# Vocelio Backend Stop Script for Windows
Write-Host "🛑 Stopping Vocelio Backend Services..." -ForegroundColor Red

# Function to stop a service
function Stop-Service {
    param([string]$ServiceName)
    
    $pidFile = "pids/$ServiceName.pid"
    
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        
        try {
            $process = Get-Process -Id $pid -ErrorAction Stop
            Write-Host "🔧 Stopping $ServiceName (PID: $pid)..." -ForegroundColor Blue
            
            Stop-Process -Id $pid -Force
            Write-Host "✅ $ServiceName stopped" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  $ServiceName was not running" -ForegroundColor Yellow
        }
        
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
    else {
        Write-Host "⚠️  No PID file found for $ServiceName" -ForegroundColor Yellow
    }
}

# Stop all services
Write-Host "🛑 Stopping all services..." -ForegroundColor Blue

# Stop services in reverse order
Stop-Service -ServiceName "Agents Service"
Stop-Service -ServiceName "API Gateway"

# Clean up any remaining Python processes on our ports
Write-Host "🧹 Cleaning up any remaining processes..." -ForegroundColor Blue

$ports = @(8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012, 8013, 8014, 8015, 8016, 8017, 8018)

foreach ($port in $ports) {
    try {
        $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue }
        
        foreach ($process in $processes) {
            if ($process.ProcessName -eq "python") {
                Write-Host "🔧 Killing Python process on port $port (PID: $($process.Id))..." -ForegroundColor Yellow
                Stop-Process -Id $process.Id -Force
            }
        }
    }
    catch {
        # Port not in use, continue
    }
}

# Clean up directories
if (Test-Path "pids") { Remove-Item "pids" -Recurse -Force }
if (Test-Path "logs") { Remove-Item "logs" -Recurse -Force }

Write-Host ""
Write-Host "✅ All Vocelio Backend Services Stopped" -ForegroundColor Green
Write-Host "💡 To start services again, run: .\scripts\start.ps1" -ForegroundColor Blue
