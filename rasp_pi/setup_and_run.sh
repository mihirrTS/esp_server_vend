#!/bin/bash

# Flask Vending Machine - Raspberry Pi Setup
# Complete setup and startup for Raspberry Pi

echo "🥧 Flask Vending Machine - Raspberry Pi Setup"
echo "========================================================"
echo "This script will:"
echo "1. Create virtual environment"
echo "2. Install Python dependencies"
echo "3. Test ESP32 connection"
echo "4. Start the Flask server"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3"
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed"

# Test ESP32 connection
echo ""
echo "🔍 Testing ESP32 connection..."
python3 -c "
try:
    from esp32_serial import ESP32SerialCommunication
    esp32 = ESP32SerialCommunication()
    if esp32.connect():
        print('✅ ESP32 found and connected!')
        esp32.disconnect()
    else:
        print('⚠️ ESP32 not found - will run in simulation mode')
        print('💡 Connect ESP32 via USB and upload ../esp32_mock_vend.ino firmware')
except Exception as e:
    print(f'⚠️ ESP32 test failed: {e}')
    print('Will run in simulation mode')
"

echo ""
echo "🚀 Starting Flask Vending Machine Server..."
echo ""
echo "========================================================"
echo "🌐 Web Interface: http://localhost:5000"
echo "📱 Mobile Access: http://$(hostname -I | cut -d' ' -f1):5000"
echo "🛑 Press Ctrl+C to stop"
echo "========================================================"
echo ""

# Run from current directory (rasp_pi)
python3 app.py