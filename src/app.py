from flask import Flask, render_template, request, jsonify
import time
from datetime import datetime
import sys
import os

app = Flask(__name__)

# Try to import ESP32 serial communication
esp32_serial = None
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from esp32_serial import ESP32SerialCommunication
    
    # For Windows, typically COM3, COM4, etc.
    # For Linux/Raspberry Pi, typically /dev/ttyUSB0
    import platform
    if platform.system() == "Windows":
        default_port = "COM3"  # Change this to your ESP32 port
    else:
        default_port = "/dev/ttyUSB0"
    
    esp32_serial = ESP32SerialCommunication(port=default_port)
    print(f"📡 ESP32 serial module loaded (port: {default_port})")
except ImportError as e:
    print(f"⚠️ ESP32 serial module not available: {e}")
except Exception as e:
    print(f"⚠️ ESP32 serial initialization error: {e}")

# In-memory storage for ESP32 devices and commands (WiFi mode)
esp32_devices = {}
pending_commands = {}
command_history = []

@app.route('/')
def index():
    """Serve the main vending machine interface"""
    return render_template('index.html')

@app.route('/vend/<int:slot_id>', methods=['POST'])
def vend(slot_id):
    """Handle vending requests for specific slots - supports both serial and WiFi"""
    try:
        # Validate slot_id
        if slot_id < 1 or slot_id > 5:
            return jsonify({
                "status": "error", 
                "message": "Invalid slot ID. Must be between 1-5",
                "slot": slot_id
            }), 400
        
        communication_used = None
        success = False
        
        # Priority 1: Try serial communication first (ESP32 via USB)
        if esp32_serial and esp32_serial.is_connected:
            success = esp32_serial.send_vend_command(slot_id)
            if success:
                communication_used = "serial"
                print(f"📡 Serial command sent to ESP32: VEND:{slot_id}")
                
                return jsonify({
                    "status": "command_sent",
                    "slot": slot_id,
                    "message": f"Serial command sent to ESP32 for slot {slot_id}",
                    "communication": "serial",
                    "device": f"USB port {esp32_serial.port}"
                }), 200
        
        # Priority 2: Check if any WiFi ESP32 devices are connected
        online_devices = [dev for dev in esp32_devices.values() if dev.get('status') == 'online']
        
        if online_devices:
            # Send command to first available ESP32 (WiFi mode)
            device_id = list(esp32_devices.keys())[0]
            
            # Store command for ESP32 to pick up
            pending_commands[device_id] = {
                "command": "VEND",
                "slot": slot_id,
                "timestamp": time.time()
            }
            
            communication_used = "wifi"
            success = True
            print(f"📡 WiFi command queued for ESP32 {device_id}: Slot {slot_id}")
            
            # Log command
            command_history.append({
                "timestamp": datetime.now().isoformat(),
                "device_id": device_id,
                "slot": slot_id,
                "status": "sent",
                "communication": "wifi"
            })
            
            return jsonify({
                "status": "command_sent",
                "slot": slot_id,
                "message": f"WiFi command sent to ESP32 for slot {slot_id}",
                "device_id": device_id,
                "communication": "wifi"
            }), 200
        
        # Priority 3: Fallback to simulation if no ESP32 connected
        if not success:
            command = f"VEND:{slot_id}"
            print(f"🖥️ No ESP32 connected - Simulating: {command}")
            print(f"Simulating vending from slot {slot_id}...")
            
            return jsonify({
                "status": "command_sent",
                "slot": slot_id,
                "message": f"Successfully sent vend command for slot {slot_id} (simulated)",
                "communication": "simulation"
            }), 200
        
    except Exception as e:
        print(f"Error processing vend request: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "slot": slot_id
        }), 500

@app.route('/status')
def status():
    """Health check endpoint - shows both serial and WiFi status"""
    serial_status = "connected" if (esp32_serial and esp32_serial.is_connected) else "disconnected"
    wifi_devices = len([d for d in esp32_devices.values() if d.get('status') == 'online'])
    
    return jsonify({
        "status": "online", 
        "message": "Vending machine is ready",
        "esp32_serial": serial_status,
        "esp32_wifi_devices": wifi_devices,
        "online_devices": wifi_devices + (1 if serial_status == "connected" else 0),
        "total_devices": len(esp32_devices) + (1 if esp32_serial else 0),
        "communication_modes": {
            "serial": {
                "status": serial_status,
                "port": esp32_serial.port if esp32_serial else "not configured"
            },
            "wifi": f"{wifi_devices} devices online"
        }
    })

# =================================
# ESP32 WiFi Communication Endpoints
# =================================

@app.route('/esp32/register', methods=['POST'])
def esp32_register():
    """Register ESP32 device with the server (WiFi mode)"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({"error": "device_id required"}), 400
        
        # Store device info
        esp32_devices[device_id] = {
            "device_id": device_id,
            "ip_address": data.get('ip_address'),
            "status": "online",
            "last_seen": time.time(),
            "slots_available": data.get('slots_available', 5),
            "communication": "wifi"
        }
        
        print(f"📱 ESP32 WiFi device registered: {device_id} ({data.get('ip_address')})")
        
        return jsonify({
            "status": "registered",
            "message": "ESP32 device registered successfully",
            "server_time": time.time()
        }), 200
        
    except Exception as e:
        print(f"Error registering ESP32: {e}")
        return jsonify({"error": "Registration failed"}), 500

@app.route('/esp32/commands/<device_id>', methods=['GET'])
def esp32_get_commands(device_id):
    """ESP32 polls for pending commands (WiFi mode)"""
    try:
        # Update last seen time
        if device_id in esp32_devices:
            esp32_devices[device_id]['last_seen'] = time.time()
        
        # Check for pending commands
        if device_id in pending_commands:
            command = pending_commands.pop(device_id)  # Remove after sending
            return jsonify(command), 200
        else:
            return jsonify(None), 200  # No commands pending
            
    except Exception as e:
        print(f"Error getting commands for {device_id}: {e}")
        return jsonify({"error": "Command retrieval failed"}), 500

@app.route('/esp32/confirm', methods=['POST'])
def esp32_confirm():
    """ESP32 sends confirmation of command execution (WiFi mode)"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        slot = data.get('slot')
        success = data.get('success')
        message = data.get('message')
        
        print(f"✅ ESP32 {device_id} - Slot {slot}: {message}")
        
        # Update command history
        for cmd in command_history:
            if cmd.get('device_id') == device_id and cmd.get('slot') == slot:
                cmd['status'] = 'completed' if success else 'failed'
                cmd['result_message'] = message
                break
        
        return jsonify({"status": "confirmation_received"}), 200
        
    except Exception as e:
        print(f"Error processing confirmation: {e}")
        return jsonify({"error": "Confirmation failed"}), 500

@app.route('/esp32/devices')
def esp32_devices_list():
    """List all registered ESP32 devices (both serial and WiFi)"""
    serial_info = []
    if esp32_serial:
        serial_info.append({
            "type": "serial",
            "port": esp32_serial.port,
            "connected": esp32_serial.is_connected,
            "device_id": f"serial_{esp32_serial.port}",
            "communication": "serial"
        })
    
    return jsonify({
        "serial_devices": serial_info,
        "wifi_devices": list(esp32_devices.values()),
        "total_devices": len(esp32_devices) + len(serial_info)
    })

@app.route('/esp32/commands/history')
def command_history_view():
    """View command history"""
    return jsonify({
        "commands": command_history[-50:],  # Last 50 commands
        "total_commands": len(command_history)
    })

if __name__ == '__main__':
    print("🏪 Flask Vending Machine Server (Hybrid Communication)")
    print("=" * 60)
    
    # Try to connect to ESP32 via serial
    if esp32_serial:
        print("🔌 Attempting to connect to ESP32 via USB serial...")
        if esp32_serial.connect():
            print(f"✅ ESP32 connected via serial (USB port: {esp32_serial.port})")
        else:
            print("❌ ESP32 not found on serial port")
            print("   Make sure ESP32 is connected via USB")
            print("   and esp32_mock_vend.ino firmware is uploaded")
    
    print("\n📡 Server will also accept WiFi ESP32 connections")
    print("   WiFi ESP32s should use esp32_wifi_vend.ino firmware")
    
    print("\n🌐 Web Interface Access:")
    print("   Local: http://localhost:5000")
    print("   Network: http://[YOUR_IP_ADDRESS]:5000")
    
    print("\n💡 Communication Priority:")
    print("   1. USB Serial (immediate)")
    print("   2. WiFi Network (polled)")
    print("   3. Simulation (fallback)")
    
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        if esp32_serial and esp32_serial.is_connected:
            esp32_serial.disconnect()
            print("🔌 ESP32 serial connection closed")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        if esp32_serial and esp32_serial.is_connected:
            esp32_serial.disconnect()