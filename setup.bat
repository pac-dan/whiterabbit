@echo off
echo ============================================
echo SnowboardMedia Quick Setup Script
echo ============================================
echo.

REM Check Python version
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Copy environment file
echo [5/6] Setting up environment file...
if exist .env (
    echo .env file already exists
) else (
    copy .env.example .env
    echo .env file created - PLEASE EDIT THIS FILE WITH YOUR API KEYS
)
echo.

REM Initialize database
echo [6/6] Initializing database...
echo.
echo Choose an option:
echo 1. Initialize empty database
echo 2. Initialize database with sample data
echo 3. Skip database setup
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    python app.py init-db
    echo Database initialized
) else if "%choice%"=="2" (
    python app.py init-db
    python app.py seed-db
    echo Database initialized with sample data
) else (
    echo Skipping database setup
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: python app.py create-admin
echo 3. Run: python app.py
echo 4. Open: http://localhost:5000
echo.
echo For detailed instructions, see docs\QUICKSTART.md
echo.
pause
