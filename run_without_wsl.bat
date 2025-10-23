@echo off
echo 🚀 Running Arabic POV Project WITHOUT WSL
echo ==========================================

REM Check if Docker Desktop is installed
echo Checking Docker Desktop...
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker is running
echo Checking if Docker is running...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    echo Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Please wait for Docker Desktop to start, then run this script again.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Navigate to project directory
cd /d "%~dp0"

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found in current directory
    echo Make sure you're running this from the project root directory.
    pause
    exit /b 1
)

echo ✅ Project files found

REM Build and start the project
echo 🐳 Building Docker image...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo ✅ Docker image built successfully

echo 🚀 Starting containers...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start containers
    pause
    exit /b 1
)

echo ✅ Project started successfully!
echo 🌐 Access your application at: http://localhost:8000
echo 📊 Check logs with: docker-compose logs -f
echo 🛑 Stop with: docker-compose down

pause
