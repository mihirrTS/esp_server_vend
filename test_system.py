#!/usr/bin/env python3
"""
Flask Vending Machine - Simple Test Script
Tests basic system functionality
"""

import sys
import os
import requests
import time

def test_system():
    """Run basic system tests"""
    print("🧪 Flask Vending Machine - Simple Test")
    print("=" * 40)
    
    # Test 1: Check if we can import ESP32 module
    print("📦 Testing ESP32 Serial Module...")
    try:
        sys.path.append('.')
        from esp32_serial import ESP32SerialCommunication
        esp32 = ESP32SerialCommunication()
        print("✅ ESP32 module imported successfully")
        
        # Try to connect
        if esp32.connect():
            print("✅ ESP32 connected via USB")
            esp32.disconnect()
        else:
            print("⚠️ ESP32 not connected (will use simulation)")
    except Exception as e:
        print(f"❌ ESP32 module error: {e}")
    
    # Test 2: Try to start Flask server check
    print("\n🌐 Testing Flask Server...")
    try:
        # Import Flask app
        from src.app import app
        print("✅ Flask app imported successfully")
        
        # Check if we can create app context
        with app.app_context():
            print("✅ Flask app context created")
            
    except Exception as e:
        print(f"❌ Flask app error: {e}")
    
    # Test 3: Check if server is running
    print("\n📡 Testing Server Connection...")
    try:
        response = requests.get("http://localhost:5000/status", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running")
            print(f"   Communication modes: {data.get('communication_modes', {})}")
        else:
            print(f"❌ Server returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running - start with: python src/app.py")
    except Exception as e:
        print(f"❌ Connection test error: {e}")
    
    print("\n" + "=" * 40)
    print("💡 To start the server: python src/app.py")
    print("💡 To open web interface: http://localhost:5000")
    print("🔌 Connect ESP32 via USB for hardware communication")

if __name__ == "__main__":
    test_system()