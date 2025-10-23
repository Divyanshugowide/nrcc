# Fix Docker Context and Environment Variables
# Run as Administrator

Write-Host "🔧 Fixing Docker Context and Environment Variables" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n📋 Step 1: Checking current Docker context..." -ForegroundColor Cyan
docker context ls

Write-Host "`n📋 Step 2: Removing DOCKER_HOST environment variable..." -ForegroundColor Cyan
try {
    # Remove DOCKER_HOST from user environment
    [Environment]::SetEnvironmentVariable("DOCKER_HOST", $null, "User")
    
    # Remove DOCKER_HOST from current session
    $env:DOCKER_HOST = $null
    
    Write-Host "✅ DOCKER_HOST environment variable removed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to remove DOCKER_HOST: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Step 3: Switching to desktop-linux context..." -ForegroundColor Cyan
try {
    docker context use desktop-linux
    Write-Host "✅ Switched to desktop-linux context" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to switch context: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Step 4: Testing Docker connection..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info 2>&1
    if ($dockerInfo -match "Server Version") {
        Write-Host "✅ Docker is working properly!" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not responding properly" -ForegroundColor Red
        Write-Host "Docker output: $dockerInfo" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Failed to test Docker: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Step 5: Testing Docker Compose..." -ForegroundColor Cyan
try {
    $composeVersion = docker-compose --version 2>&1
    if ($composeVersion -match "Docker Compose version") {
        Write-Host "✅ Docker Compose is working!" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker Compose is not working" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to test Docker Compose: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Docker Context Fix Complete!" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Close and reopen PowerShell" -ForegroundColor White
Write-Host "2. Run: docker info" -ForegroundColor White
Write-Host "3. Run: docker-compose up -d" -ForegroundColor White

Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
Read-Host
