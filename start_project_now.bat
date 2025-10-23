@echo off
echo 🚀 Starting Arabic POV Project - Quick Fix
echo ==========================================

REM Clear DOCKER_HOST environment variable
set DOCKER_HOST=

REM Switch to desktop-linux context
echo Switching to desktop-linux context...
docker context use desktop-linux

REM Test Docker
echo Testing Docker connection...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Please wait for Docker Desktop to start, then run this script again.
    pause
    exit /b 1
)

echo ✅ Docker is working!

REM Navigate to project directory
cd /d "%~dp0"

REM Build the project
echo 🐳 Building Docker image...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    echo Trying alternative approach...
    
    REM Try building with docker build instead
    echo Building with docker build...
    docker build -t nrrc-arabic-pov .
    
    if %errorlevel% neq 0 (
        echo ❌ Docker build still failed
        pause
        exit /b 1
    )
)

echo ✅ Docker image built successfully!

REM Start the project
echo 🚀 Starting containers...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start containers
    echo Trying to start manually...
    
    REM Try starting with docker run
    echo Starting with docker run...
    docker run -d -p 8000:8000 --name nrrc-arabic-pov nrrc-arabic-pov
    
    if %errorlevel% neq 0 (
        echo ❌ Failed to start container
        pause
        exit /b 1
    )
)

echo ✅ Project started successfully!
echo 🌐 Access your application at: http://localhost:8000
echo 📊 Check logs with: docker-compose logs -f
echo 🛑 Stop with: docker-compose down

echo.
echo Press any key to open the application in your browser...
pause >nul
start http://localhost:8000
