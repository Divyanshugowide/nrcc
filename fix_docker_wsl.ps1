# Quick Fix for Docker WSL Issues
# Run this as Administrator

Write-Host "🔧 Quick Fix for Docker WSL Issues" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Step 1: Stop all WSL instances
Write-Host "`n🛑 Stopping all WSL instances..." -ForegroundColor Cyan
wsl --shutdown
Start-Sleep -Seconds 3

# Step 2: Check WSL status
Write-Host "`n📋 Checking WSL status..." -ForegroundColor Cyan
wsl --list --verbose

# Step 3: Start Ubuntu WSL
Write-Host "`n🚀 Starting Ubuntu WSL..." -ForegroundColor Cyan
try {
    wsl --distribution Ubuntu --exec echo "WSL is working"
    Write-Host "✅ WSL is working" -ForegroundColor Green
} catch {
    Write-Host "❌ WSL failed to start" -ForegroundColor Red
    Write-Host "Trying to fix WSL..." -ForegroundColor Yellow
    
    # Try to repair WSL
    wsl --unregister Ubuntu
    wsl --install Ubuntu
}

# Step 4: Check Docker Desktop
Write-Host "`n🐳 Checking Docker Desktop..." -ForegroundColor Cyan
if (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} else {
    Write-Host "⚠️ Docker Desktop is not running" -ForegroundColor Yellow
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 10
}

# Step 5: Test Docker in WSL
Write-Host "`n🧪 Testing Docker in WSL..." -ForegroundColor Cyan
try {
    $dockerTest = wsl --distribution Ubuntu --exec docker --version 2>&1
    if ($dockerTest -match "Docker version") {
        Write-Host "✅ Docker is working in WSL" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker not working in WSL" -ForegroundColor Red
        Write-Host "Installing Docker in WSL..." -ForegroundColor Yellow
        
        # Install Docker in WSL
        $installDocker = @"
sudo apt update
sudo apt install -y docker.io
sudo usermod -aG docker `$USER
sudo service docker start
"@
        wsl --distribution Ubuntu --exec bash -c $installDocker
    }
} catch {
    Write-Host "❌ Failed to test Docker in WSL" -ForegroundColor Red
}

# Step 6: Test Docker Compose
Write-Host "`n🔧 Testing Docker Compose..." -ForegroundColor Cyan
try {
    $composeTest = wsl --distribution Ubuntu --exec docker-compose --version 2>&1
    if ($composeTest -match "docker-compose version") {
        Write-Host "✅ Docker Compose is working" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Docker Compose not found, installing..." -ForegroundColor Yellow
        
        # Install Docker Compose
        $installCompose = @"
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
"@
        wsl --distribution Ubuntu --exec bash -c $installCompose
    }
} catch {
    Write-Host "❌ Failed to install Docker Compose" -ForegroundColor Red
}

# Step 7: Test your project
Write-Host "`n🚀 Testing your Arabic POV project..." -ForegroundColor Cyan
try {
    # Change to project directory in WSL
    $projectPath = "/mnt/d/nrrc_arabic_pov_windows"
    
    # Test if project files exist
    $testFiles = wsl --distribution Ubuntu --exec bash -c "ls -la $projectPath/docker-compose.yml" 2>&1
    if ($testFiles -match "docker-compose.yml") {
        Write-Host "✅ Project files found" -ForegroundColor Green
        
        # Try to build the project
        Write-Host "Building Docker image..." -ForegroundColor Yellow
        $buildResult = wsl --distribution Ubuntu --exec bash -c "cd $projectPath && docker-compose build" 2>&1
        
        if ($buildResult -match "Successfully built" -or $buildResult -match "Successfully tagged") {
            Write-Host "✅ Docker build successful!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Docker build had issues, but continuing..." -ForegroundColor Yellow
            Write-Host "Build output: $buildResult" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Project files not found at $projectPath" -ForegroundColor Red
        Write-Host "Make sure your project is in D:\nrrc_arabic_pov_windows" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to test project" -ForegroundColor Red
}

# Final instructions
Write-Host "`n🎉 Docker WSL Fix Complete!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open WSL: wsl" -ForegroundColor White
Write-Host "2. Navigate to project: cd /mnt/d/nrrc_arabic_pov_windows" -ForegroundColor White
Write-Host "3. Run project: docker-compose up -d" -ForegroundColor White
Write-Host "4. Access at: http://localhost:8000" -ForegroundColor White

Write-Host "`nIf you still have issues:" -ForegroundColor Red
Write-Host "- Restart Docker Desktop" -ForegroundColor Yellow
Write-Host "- Restart WSL: wsl --shutdown" -ForegroundColor Yellow
Write-Host "- Check Docker Desktop WSL 2 integration settings" -ForegroundColor Yellow
