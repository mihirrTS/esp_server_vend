#!/bin/bash

# Flask Vending Machine - Raspberry Pi Setup
# Sets up the development environment

echo "🥧 Flask Vending Machine - Setup (Raspberry Pi)"
echo "==============================================="
echo "This script will set up your vending machine environment:"
echo "1. Check Python 3 installation"
echo "2. Create virtual environment (if needed)"
echo "3. Install Python dependencies (if needed)"
echo "4. Test system components"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing..."
    sudo apt update
    sudo apt install python3 python3-pip python3-venv -y
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Python 3"
        exit 1
    fi
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
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are already installed
echo ""
echo "🔍 Checking dependencies..."
python3 -c "import flask, serial, requests" &> /dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check dialout group membership for serial communication
if ! groups | grep -q dialout; then
    echo ""
    echo "🔧 Adding user to dialout group for ESP32 communication..."
    sudo usermod -a -G dialout $USER
    echo "⚠️ Please logout and login again for group changes to take effect"
fi

echo ""
echo "🧪 Running system test..."
python3 test_system.py

echo ""
echo "================================================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Connect ESP32 via USB (optional - runs in simulation without)"
echo "2. Run: ./start.sh (to start the server)"
echo "3. Open: http://localhost:5000 (web interface)"
echo ""
echo "Files created:"
echo "- venv/          (Python virtual environment)"
echo "- Python packages installed in virtual environment"
echo "================================================================"
echo ""