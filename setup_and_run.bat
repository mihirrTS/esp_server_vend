@echo off
echo 🏪 Flask Vending Machine - Complete Setup (Windows)
echo =========================================================
echo This script will:
echo 1. Create virtual environment
echo 2. Install Python dependencies  
echo 3. Test ESP32 connection
echo 4. Start the Flask server
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
    echo ✅ Virtual environment found
)

echo.
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed

REM Test ESP32 connection
echo.
echo 🔍 Testing ESP32 connection...
python -c "
try:
    from esp32_serial import ESP32SerialCommunication
    esp32 = ESP32SerialCommunication()
    if esp32.connect():
        print('✅ ESP32 found and connected!')
        esp32.disconnect()
    else:
        print('⚠️ ESP32 not found - will run in simulation mode')
        print('💡 Connect ESP32 via USB and upload esp32_mock_vend.ino firmware')
except Exception as e:
    print(f'⚠️ ESP32 test failed: {e}')
    print('Will run in simulation mode')
"

echo.
echo 🚀 Starting Flask Vending Machine Server...
echo.
echo =========================================================
echo 🌐 Web Interface: http://localhost:5000
echo 📱 Mobile Access: http://[YOUR_IP]:5000
echo 🛑 Press Ctrl+C to stop
echo =========================================================
echo.

cd src
python app.py

echo.
echo 👋 Server stopped. Press any key to exit...
pause >nul