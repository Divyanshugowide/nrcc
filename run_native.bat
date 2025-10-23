@echo off
echo 🐍 Running Arabic POV Project Natively (No Docker)
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo ✅ Virtual environment ready

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Check if data exists
if not exist "data\idx\bm25.pkl" (
    echo ❌ Data indices not found. Please run the processing scripts first:
    echo 1. python scripts\02_extract_and_chunk.py
    echo 2. python scripts\03_build_bm25.py
    echo 3. python scripts\04_build_faiss.py
    pause
    exit /b 1
)

echo ✅ Data indices found

REM Start the application
echo 🚀 Starting Arabic POV application...
echo 🌐 The application will be available at: http://localhost:8000
echo 🛑 Press Ctrl+C to stop the application
echo.

uvicorn app.run_api:app --host 0.0.0.0 --port 8000 --reload
