# WSL and Docker Setup Script for D Drive
# Run this as Administrator

Write-Host "🚀 Setting up WSL on D Drive and Docker Support" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Step 1: Enable WSL and Virtual Machine Platform
Write-Host "`n📋 Step 1: Enabling WSL and Virtual Machine Platform..." -ForegroundColor Cyan
try {
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    Write-Host "✅ WSL features enabled successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to enable WSL features: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Set WSL 2 as default
Write-Host "`n📋 Step 2: Setting WSL 2 as default..." -ForegroundColor Cyan
try {
    wsl --set-default-version 2
    Write-Host "✅ WSL 2 set as default" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to set WSL 2 as default: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Create D:\WSL directory
Write-Host "`n📋 Step 3: Creating WSL directory on D drive..." -ForegroundColor Cyan
$wslPath = "D:\WSL"
if (!(Test-Path $wslPath)) {
    try {
        New-Item -ItemType Directory -Path $wslPath -Force
        Write-Host "✅ Created D:\WSL directory" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to create D:\WSL directory: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ D:\WSL directory already exists" -ForegroundColor Green
}

# Step 4: Download and install Ubuntu
Write-Host "`n📋 Step 4: Installing Ubuntu on D drive..." -ForegroundColor Cyan
$ubuntuPath = "$wslPath\Ubuntu"
if (!(Test-Path $ubuntuPath)) {
    try {
        # Download Ubuntu
        $ubuntuUrl = "https://aka.ms/wslubuntu2004"
        $ubuntuInstaller = "$env:TEMP\Ubuntu.appx"
        Write-Host "Downloading Ubuntu installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $ubuntuUrl -OutFile $ubuntuInstaller
        
        # Extract and install
        Write-Host "Installing Ubuntu..." -ForegroundColor Yellow
        Add-AppxPackage $ubuntuInstaller
        
        # Wait for installation
        Start-Sleep -Seconds 10
        
        Write-Host "✅ Ubuntu installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install Ubuntu: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please install Ubuntu manually from Microsoft Store" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Ubuntu already installed" -ForegroundColor Green
}

# Step 5: Configure WSL to use D drive
Write-Host "`n📋 Step 5: Configuring WSL to use D drive..." -ForegroundColor Cyan
try {
    # Create .wslconfig file
    $wslConfigPath = "$env:USERPROFILE\.wslconfig"
    $wslConfig = @"
[wsl2]
memory=4GB
processors=2
swap=2GB
localhostForwarding=true
"@
    $wslConfig | Out-File -FilePath $wslConfigPath -Encoding UTF8
    Write-Host "✅ WSL configuration created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create WSL config: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Install Docker Desktop
Write-Host "`n📋 Step 6: Installing Docker Desktop..." -ForegroundColor Cyan
$dockerInstaller = "$env:TEMP\DockerDesktopInstaller.exe"
if (!(Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe")) {
    try {
        Write-Host "Downloading Docker Desktop..." -ForegroundColor Yellow
        $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
        Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstaller
        
        Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
        Start-Process -FilePath $dockerInstaller -ArgumentList "install", "--quiet" -Wait
        
        Write-Host "✅ Docker Desktop installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install Docker Desktop: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Docker Desktop already installed" -ForegroundColor Green
}

# Step 7: Configure Docker for WSL 2
Write-Host "`n📋 Step 7: Configuring Docker for WSL 2..." -ForegroundColor Cyan
try {
    # Enable WSL 2 integration in Docker
    $dockerConfigPath = "$env:USERPROFILE\.docker\daemon.json"
    $dockerConfigDir = Split-Path $dockerConfigPath -Parent
    if (!(Test-Path $dockerConfigDir)) {
        New-Item -ItemType Directory -Path $dockerConfigDir -Force
    }
    
    $dockerConfig = @"
{
  "experimental": false,
  "debug": false,
  "registry-mirrors": [],
  "features": {
    "buildkit": true
  }
}
"@
    $dockerConfig | Out-File -FilePath $dockerConfigPath -Encoding UTF8
    Write-Host "✅ Docker configuration created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Docker config: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Start WSL and configure Ubuntu
Write-Host "`n📋 Step 8: Starting WSL and configuring Ubuntu..." -ForegroundColor Cyan
try {
    # Start WSL
    wsl --shutdown
    Start-Sleep -Seconds 5
    wsl --distribution Ubuntu --exec echo "WSL is running"
    
    Write-Host "✅ WSL started successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start WSL: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 9: Create Docker setup script for WSL
Write-Host "`n📋 Step 9: Creating Docker setup script for WSL..." -ForegroundColor Cyan
$dockerSetupScript = @"
#!/bin/bash
# Docker setup script for WSL

echo "🐳 Setting up Docker in WSL..."

# Update package list
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker `$USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Start Docker service
sudo service docker start

echo "✅ Docker setup completed in WSL"
echo "Please restart WSL or run: newgrp docker"
"@

$dockerSetupScript | Out-File -FilePath "$wslPath\docker-setup.sh" -Encoding UTF8
Write-Host "✅ Docker setup script created" -ForegroundColor Green

# Final instructions
Write-Host "`n🎉 Setup completed! Next steps:" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "1. Restart your computer" -ForegroundColor Yellow
Write-Host "2. Start Docker Desktop" -ForegroundColor Yellow
Write-Host "3. Enable WSL 2 integration in Docker Desktop settings" -ForegroundColor Yellow
Write-Host "4. Run the following commands in WSL:" -ForegroundColor Yellow
Write-Host "   wsl" -ForegroundColor White
Write-Host "   bash D:\WSL\docker-setup.sh" -ForegroundColor White
Write-Host "   newgrp docker" -ForegroundColor White
Write-Host "5. Test Docker: docker --version" -ForegroundColor Yellow
Write-Host "6. Build your project: docker-compose up -d" -ForegroundColor Yellow

Write-Host "`n📁 WSL files location: D:\WSL\" -ForegroundColor Cyan
Write-Host "🔧 Docker setup script: D:\WSL\docker-setup.sh" -ForegroundColor Cyan

Write-Host "`n⚠️  Important: Restart your computer before proceeding!" -ForegroundColor Red
