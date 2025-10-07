#!/bin/bash

# Flask Vending Machine - Raspberry Pi Start Server
# Starts the Flask server

echo "🥧 Flask Vending Machine - Start Server"
echo "======================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run: ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Quick dependency check
python3 -c "import flask, serial, requests" &> /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not found"
    echo "Please run: ./setup.sh first"
    exit 1
fi

echo ""
echo "🚀 Starting Flask Vending Machine Server..."
echo ""
echo "========================================================"
echo "🌐 Local Access: http://localhost:5000"
echo "📱 Network Access: http://$(hostname -I | cut -d' ' -f1):5000"
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================================"
echo ""

# Run from current directory (rasp_pi)
python3 app.py