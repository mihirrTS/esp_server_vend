#!/usr/bin/env python3
"""
Raspberry Pi Vending Machine - Simple Test Script
Tests Pi-specific functionality
"""

import sys
import os
import requests
import time

def test_pi_system():
    """Run Raspberry Pi system tests"""
    print("🥧 Raspberry Pi Vending Machine - Simple Test")
    print("=" * 45)
    
    # Test 1: Check if we can import ESP32 module
    print("📦 Testing ESP32 Serial Module...")
    try:
        from esp32_serial import ESP32SerialCommunication
        esp32 = ESP32SerialCommunication()
        print("✅ ESP32 module imported successfully")
        
        # Try to connect
        if esp32.connect():
            print(f"✅ ESP32 connected on port: {esp32.port}")
            # Send test command
            if esp32.send_command("STATUS"):
                print("✅ ESP32 communication test successful")
            esp32.disconnect()
        else:
            print("⚠️ ESP32 not connected (will use simulation)")
            print("💡 Connect ESP32 via USB to Raspberry Pi")
    except Exception as e:
        print(f"❌ ESP32 module error: {e}")
    
    # Test 2: Check Pi-specific serial ports
    print("\n🔌 Checking Raspberry Pi Serial Ports...")
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if ports:
            print(f"✅ Found {len(ports)} serial port(s):")
            for port in ports:
                print(f"   📍 {port.device}: {port.description}")
        else:
            print("⚠️ No serial ports found")
            print("💡 Connect ESP32 via USB cable")
    except Exception as e:
        print(f"❌ Port detection error: {e}")
    
    # Test 3: Try to start Flask server check  
    print("\n🌐 Testing Pi Flask Server...")
    try:
        from app import app
        print("✅ Pi Flask app imported successfully")
        
        with app.app_context():
            print("✅ Pi Flask app context created")
            
    except Exception as e:
        print(f"❌ Pi Flask app error: {e}")
    
    # Test 4: Check if server is running
    print("\n📡 Testing Pi Server Connection...")
    try:
        response = requests.get("http://localhost:5000/status", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("✅ Pi server is running")
            print(f"   Platform: Raspberry Pi")
            print(f"   Communication modes: {data.get('communication_modes', {})}")
            print(f"   ESP32 devices: {data.get('esp32_serial', 'unknown')}")
        else:
            print(f"❌ Server returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running - start with: python3 app.py")
    except Exception as e:
        print(f"❌ Connection test error: {e}")
    
    # Test 5: Check network access
    print("\n🌐 Testing Network Access...")
    try:
        import subprocess
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ip_address = result.stdout.strip().split()[0]
            print(f"✅ Pi IP Address: {ip_address}")
            print(f"🌐 Network access: http://{ip_address}:5000")
        else:
            print("⚠️ Could not determine IP address")
    except Exception as e:
        print(f"❌ Network test error: {e}")
    
    print("\n" + "=" * 45)
    print("💡 To start the server: python3 app.py")
    print("💡 To open web interface: http://localhost:5000")
    print("📱 Mobile access: http://[PI_IP]:5000")
    print("🔌 Connect ESP32 via USB for hardware communication")
    print("⚙️ Run setup script: ./setup_and_run.sh")

if __name__ == "__main__":
    test_pi_system()