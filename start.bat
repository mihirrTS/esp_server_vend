@echo off
echo 🏪 Flask Vending Machine - Start Server
echo =======================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found
    echo Please run: setup.bat first
    pause
    exit /b 1
)

echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Quick dependency check
python -c "import flask, serial, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dependencies not found
    echo Please run: setup.bat first
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Flask Vending Machine Server...
echo.
echo =========================================================
echo 🌐 Web Interface: http://localhost:5000
echo 📱 Network Access: http://[YOUR_IP]:5000
echo 🛑 Press Ctrl+C to stop the server
echo =========================================================
echo.

cd src
python app.py

echo.
echo 👋 Server stopped. Press any key to exit...
pause >nul