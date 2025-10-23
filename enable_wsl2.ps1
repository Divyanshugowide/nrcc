# Enable WSL2 and Fix Docker Issues
# Run as Administrator

Write-Host "🔧 Enabling WSL2 and Fixing Docker Issues" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n📋 Step 1: Enabling Windows Features..." -ForegroundColor Cyan

# Enable WSL
Write-Host "Enabling Windows Subsystem for Linux..." -ForegroundColor Yellow
try {
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    Write-Host "✅ WSL enabled" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to enable WSL: $($_.Exception.Message)" -ForegroundColor Red
}

# Enable Virtual Machine Platform
Write-Host "Enabling Virtual Machine Platform..." -ForegroundColor Yellow
try {
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    Write-Host "✅ Virtual Machine Platform enabled" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to enable Virtual Machine Platform: $($_.Exception.Message)" -ForegroundColor Red
}

# Enable Hyper-V
Write-Host "Enabling Hyper-V..." -ForegroundColor Yellow
try {
    dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart
    Write-Host "✅ Hyper-V enabled" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Hyper-V may already be enabled or not available on this system" -ForegroundColor Yellow
}

Write-Host "`n📋 Step 2: Updating WSL..." -ForegroundColor Cyan
try {
    wsl --update
    Write-Host "✅ WSL updated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update WSL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Step 3: Setting WSL2 as default..." -ForegroundColor Cyan
try {
    wsl --set-default-version 2
    Write-Host "✅ WSL2 set as default" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to set WSL2 as default: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Step 4: Installing Ubuntu..." -ForegroundColor Cyan
try {
    wsl --install Ubuntu --no-launch
    Write-Host "✅ Ubuntu installation initiated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Ubuntu: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 Step 5: Checking WSL status..." -ForegroundColor Cyan
try {
    wsl --status
    Write-Host "✅ WSL status checked" -ForegroundColor Green
} catch {
    Write-Host "❌ WSL status check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 WSL2 Setup Complete!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "`n⚠️  IMPORTANT: You must restart your computer now!" -ForegroundColor Red
Write-Host "After restart:" -ForegroundColor Yellow
Write-Host "1. Run: wsl --install Ubuntu" -ForegroundColor White
Write-Host "2. Run: fix_docker_wsl.ps1" -ForegroundColor White
Write-Host "3. Run: run_docker_project.bat" -ForegroundColor White

Write-Host "`nPress any key to restart your computer..." -ForegroundColor Yellow
Read-Host

# Restart computer
Write-Host "Restarting computer in 10 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Restart-Computer -Force
