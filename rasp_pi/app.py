from flask import Flask, render_template, request, jsonify
import time
from datetime import datetime
import sys
import os

app = Flask(__name__)

# Try to import ESP32 serial communication
esp32_serial = None
try:
    from esp32_serial import ESP32SerialCommunication
    # For Raspberry Pi, typically /dev/ttyUSB0 or /dev/ttyACM0
    esp32_serial = ESP32SerialCommunication(port='/dev/ttyUSB0')
    print("📡 ESP32 serial module loaded")
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
    """Handle vending requests for specific slots"""
    try:
        # Validate slot_id
        if slot_id < 1 or slot_id > 5:
            return jsonify({
                "status": "error", 
                "message": "Invalid slot ID. Must be between 1-5",
                "slot": slot_id
            }), 400
        
        # Try serial communication first (ESP32 via USB)
        if esp32_serial and esp32_serial.is_connected:
            success = esp32_serial.send_vend_command(slot_id)
            if success:
                print(f"📡 Serial command sent to ESP32: VEND:{slot_id}")
                return jsonify({
                    "status": "command_sent",
                    "slot": slot_id,
                    "message": f"Serial command sent to ESP32 for slot {slot_id}",
                    "communication": "serial"
                }), 200
        
        # Check if any WiFi ESP32 devices are connected
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
            
            print(f"📡 WiFi command queued for ESP32 {device_id}: Slot {slot_id}")
            
            # Log command
            command_history.append({
                "timestamp": datetime.now().isoformat(),
                "device_id": device_id,
                "slot": slot_id,
                "status": "sent"
            })
            
            return jsonify({
                "status": "command_sent",
                "slot": slot_id,
                "message": f"WiFi command sent to ESP32 for slot {slot_id}",
                "device_id": device_id,
                "communication": "wifi"
            }), 200
        else:
            # Fallback to simulation if no ESP32 connected
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
    """Health check endpoint"""
    serial_status = "connected" if (esp32_serial and esp32_serial.is_connected) else "disconnected"
    wifi_devices = len([d for d in esp32_devices.values() if d.get('status') == 'online'])
    
    return jsonify({
        "status": "online", 
        "message": "Vending machine is ready",
        "esp32_serial": serial_status,
        "esp32_wifi_devices": wifi_devices,
        "total_devices": len(esp32_devices),
        "communication_modes": {
            "serial": serial_status,
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
            "slots_available": data.get('slots_available', 5)
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
    """List all registered ESP32 devices"""
    serial_info = []
    if esp32_serial:
        serial_info.append({
            "type": "serial",
            "port": esp32_serial.port,
            "connected": esp32_serial.is_connected,
            "device_id": f"serial_{esp32_serial.port}"
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
    print("🥧 Raspberry Pi Vending Machine Server")
    print("=" * 50)
    
    # Try to connect to ESP32 via serial
    if esp32_serial:
        print("🔌 Attempting to connect to ESP32 via USB...")
        if esp32_serial.connect():
            print("✅ ESP32 connected via serial (USB)")
        else:
            print("❌ ESP32 not found on serial port")
            print("   Make sure ESP32 is connected via USB")
            print("   and the correct port is configured")
    
    print("\n🌐 Server will also accept WiFi ESP32 connections")
    print("📍 Access the interface at:")
    print("   Local: http://localhost:5000")
    print("   Network: http://[PI_IP_ADDRESS]:5000")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        if esp32_serial and esp32_serial.is_connected:
            esp32_serial.disconnect()
            print("🔌 ESP32 serial connection closed")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        if esp32_serial and esp32_serial.is_connected:
            esp32_serial.disconnect()