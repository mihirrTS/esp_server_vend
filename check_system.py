#!/usr/bin/env python3
"""
Flask Vending Machine - System Check & Test Script
Tests system functionality and validates ESP32 connections
"""

import sys
import os
import requests
import time
import platform

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_status(message, status="info"):
    """Print status with appropriate emoji"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "test": "🧪"
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")

def test_python_environment():
    """Test Python environment and dependencies"""
    print_header("Python Environment Check")
    
    # Python version
    python_version = sys.version
    print_status(f"Python version: {python_version}", "info")
    
    if sys.version_info < (3, 7):
        print_status("Python 3.7+ required", "error")
        return False
    else:
        print_status("Python version compatible", "success")
    
    # Required modules
    required_modules = [
        ('flask', 'Flask web framework'),
        ('serial', 'PySerial for ESP32 communication'),
        ('requests', 'HTTP requests library')
    ]
    
    missing_modules = []
    for module, description in required_modules:
        try:
            __import__(module)
            print_status(f"{module}: {description} - Available", "success")
        except ImportError:
            print_status(f"{module}: {description} - Missing", "error")
            missing_modules.append(module)
    
    if missing_modules:
        print_status("Install missing modules with: pip install " + " ".join(missing_modules), "warning")
        return False
    
    return True

def test_esp32_module():
    """Test ESP32 Serial Module"""
    print_header("ESP32 Communication Module Test")
    
    try:
        sys.path.append('.')
        from esp32_serial import ESP32SerialCommunication
        print_status("ESP32 module imported successfully", "success")
        
        # Create ESP32 instance
        esp32 = ESP32SerialCommunication()
        print_status("ESP32 communication instance created", "success")
        
        # Test port scanning
        print_status("Scanning for available serial ports...", "info")
        ports = esp32.scan_ports()
        
        if ports:
            print_status(f"Found {len(ports)} serial ports:", "info")
            for port in ports:
                likely_esp32 = "🎯 (likely ESP32)" if port.get('likely_esp32') else ""
                available = "✅" if port.get('available') else "❌ (in use)"
                print(f"    {port['device']} - {port['description']} {available} {likely_esp32}")
        else:
            print_status("No serial ports found", "warning")
        
        # Test auto-detection
        print_status("Testing ESP32 auto-detection...", "info")
        detected_port = esp32._auto_detect_port()
        
        if detected_port:
            print_status(f"ESP32 auto-detected on: {detected_port}", "success")
            
            # Try to connect
            if esp32.connect(detected_port):
                print_status("ESP32 connected successfully", "success")
                print_status("Testing basic communication...", "info")
                
                # Test communication
                if esp32.is_connected:
                    print_status("ESP32 communication verified", "success")
                
                esp32.disconnect()
                print_status("ESP32 disconnected", "info")
            else:
                print_status("Could not connect to ESP32", "warning")
        else:
            print_status("No ESP32 detected via auto-detection", "warning")
            print_status("ESP32 will run in simulation mode", "info")
        
        return True
        
    except Exception as e:
        print_status(f"ESP32 module error: {e}", "error")
        return False

def test_flask_app():
    """Test Flask Application"""
    print_header("Flask Application Test")
    
    try:
        # Import Flask app
        from src.app import app
        print_status("Flask app imported successfully", "success")
        
        # Check if we can create app context
        with app.app_context():
            print_status("Flask app context created", "success")
            
        # Test app configuration
        print_status(f"Flask debug mode: {app.debug}", "info")
        print_status("Flask app configuration valid", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Flask app error: {e}", "error")
        return False

def test_server_connection():
    """Test Server Connection"""
    print_header("Server Connection Test")
    
    try:
        print_status("Attempting to connect to Flask server...", "info")
        response = requests.get("http://localhost:5000/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_status("Server is running and responsive", "success")
            
            # Display server status
            print_status("Server Status Details:", "info")
            print(f"    Total devices: {data.get('total_devices', 0)}")
            print(f"    Online devices: {data.get('online_devices', 0)}")
            print(f"    Serial status: {data.get('esp32_serial', 'unknown')}")
            print(f"    WiFi devices: {data.get('esp32_wifi_devices', 0)}")
            
            # Test communication mode
            mode_response = requests.get("http://localhost:5000/esp32/communication/mode", timeout=3)
            if mode_response.status_code == 200:
                mode_data = mode_response.json()
                current_mode = mode_data.get('current_mode', 'none')
                print_status(f"Current communication mode: {current_mode}", "info")
                
            # Test device list
            devices_response = requests.get("http://localhost:5000/esp32/devices/list", timeout=3)
            if devices_response.status_code == 200:
                devices_data = devices_response.json()
                devices = devices_data.get('devices', [])
                print_status(f"Detected {len(devices)} devices:", "info")
                for device in devices:
                    status_icon = "🟢" if device.get('connected') else "🔴"
                    device_type = device.get('type', 'unknown').upper()
                    device_id = device.get('device_id', 'unknown')
                    print(f"    {status_icon} {device_type}: {device_id}")
            
            return True
        else:
            print_status(f"Server returned status {response.status_code}", "error")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status("Server not running", "warning")
        print_status("Start server with: python src/app.py", "info")
        return False
    except Exception as e:
        print_status(f"Connection test error: {e}", "error")
        return False

def test_system_requirements():
    """Test system requirements"""
    print_header("System Requirements Check")
    
    # Operating system
    os_name = platform.system()
    print_status(f"Operating System: {os_name}", "info")
    
    # Platform specific checks
    if os_name == "Windows":
        print_status("Windows detected - USB drivers may be needed for ESP32", "info")
    elif os_name == "Linux":
        print_status("Linux detected - may need to add user to dialout group", "info")
    elif os_name == "Darwin":
        print_status("macOS detected - should work with built-in drivers", "info")
    
    # Check current directory
    current_dir = os.getcwd()
    expected_files = ['src/app.py', 'esp32_serial.py', 'requirements.txt']
    
    missing_files = []
    for file in expected_files:
        if os.path.exists(file):
            print_status(f"Found: {file}", "success")
        else:
            print_status(f"Missing: {file}", "error")
            missing_files.append(file)
    
    if missing_files:
        print_status("Some required files are missing", "error")
        return False
    
    print_status("All required files present", "success")
    return True

def run_comprehensive_test():
    """Run all system tests"""
    print_header("Flask Vending Machine - System Check")
    print("This script validates your system setup and ESP32 connections")
    
    tests = [
        ("System Requirements", test_system_requirements),
        ("Python Environment", test_python_environment), 
        ("ESP32 Module", test_esp32_module),
        ("Flask Application", test_flask_app),
        ("Server Connection", test_server_connection)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print_status(f"Running {test_name} test...", "test")
        results[test_name] = test_func()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "success" if result else "error"
        print_status(f"{test_name}: {'PASSED' if result else 'FAILED'}", status)
    
    print_status(f"\nOverall: {passed}/{total} tests passed", 
                "success" if passed == total else "warning")
    
    # Recommendations
    print_header("Recommendations")
    
    if results.get("Server Connection", False):
        print_status("✅ System is ready! Open http://localhost:5000 to use the vending machine", "success")
    elif results.get("Flask Application", False):
        print_status("🚀 Start the server with: python src/app.py", "info")
    else:
        print_status("🔧 Fix the failed tests above before proceeding", "warning")
    
    if not results.get("ESP32 Module", False):
        print_status("📱 Connect ESP32 via USB for hardware control", "info")
        print_status("💡 System will work in simulation mode without ESP32", "info")

if __name__ == "__main__":
    run_comprehensive_test()