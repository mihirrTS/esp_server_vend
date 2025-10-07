@echo off
echo 🏪 Flask Vending Machine - Setup (Windows)
echo ===============================================
echo This script will set up your vending machine environment:
echo 1. Check Python installation
echo 2. Create virtual environment (if needed)
echo 3. Install Python dependencies (if needed)
echo 4. Test system components
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are already installed
echo.
echo 🔍 Checking dependencies...
python -c "import flask, serial, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    echo ✅ Dependencies processed
) else (
    echo ✅ Dependencies already installed
)

echo.
echo 🧪 Running system test...
python test_system.py

echo.
echo ================================================================
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Connect ESP32 via USB (optional - runs in simulation without)
echo 2. Run: start.bat (to start the server)
echo 3. Open: http://localhost:5000 (web interface)
echo.
echo Files created:
echo - venv\          (Python virtual environment)
echo - Python packages installed in virtual environment
echo ================================================================
echo.
pause