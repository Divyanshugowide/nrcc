@echo off
echo 🚀 Starting Arabic POV Project with Docker
echo ==========================================

REM Check if WSL is running
echo Checking WSL status...
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL is not running. Starting WSL...
    wsl --shutdown
    timeout /t 3 /nobreak >nul
    wsl --distribution Ubuntu --exec echo "WSL started"
)

REM Check if Docker is running
echo Checking Docker...
wsl --distribution Ubuntu --exec docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found in WSL. Installing...
    wsl --distribution Ubuntu --exec bash -c "sudo apt update && sudo apt install -y docker.io && sudo usermod -aG docker $USER && sudo service docker start"
)

REM Check if Docker Compose is available
echo Checking Docker Compose...
wsl --distribution Ubuntu --exec docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose not found. Installing...
    wsl --distribution Ubuntu --exec bash -c "sudo curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose"
)

REM Navigate to project directory and start
echo 🐳 Starting Docker containers...
wsl --distribution Ubuntu --exec bash -c "cd /mnt/d/nrrc_arabic_pov_windows && docker-compose up -d"

if %errorlevel% equ 0 (
    echo ✅ Project started successfully!
    echo 🌐 Access your application at: http://localhost:8000
    echo 📊 Check logs with: wsl -d Ubuntu -e bash -c "cd /mnt/d/nrrc_arabic_pov_windows && docker-compose logs -f"
) else (
    echo ❌ Failed to start project
    echo 🔧 Try running the fix script: fix_docker_wsl.ps1
)

pause
