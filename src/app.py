from flask import Flask, render_template, request, jsonify
import time
from datetime import datetime
import sys
import os

app = Flask(__name__)

# ESP32 communication log (for real-time monitoring)
esp32_comm_log = []
MAX_LOG_ENTRIES = 100

def log_esp32_communication(direction, message, msg_type="info", device_id=None, device_type=None):
    """Log ESP32 communication for monitoring with device information"""
    global esp32_comm_log
    
    log_entry = {
        "timestamp": time.time(),
        "direction": direction,  # "sent" or "received"
        "message": message,
        "type": msg_type,  # "info", "vend", "status", "error", "success"
        "formatted_time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "device_id": device_id or "unknown",
        "device_type": device_type or "unknown"  # "serial" or "wifi"
    }
    
    esp32_comm_log.append(log_entry)
    
    # Keep only recent entries
    if len(esp32_comm_log) > MAX_LOG_ENTRIES:
        esp32_comm_log = esp32_comm_log[-MAX_LOG_ENTRIES:]

# Try to import ESP32 serial communication
esp32_serial = None
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from esp32_serial import ESP32SerialCommunication
    
        # Auto-detect ESP32 port dynamically (any port, any ESP32)
    import platform
    import serial
    
    # Create ESP32 communication instance with auto-detection
    esp32_serial = ESP32SerialCommunication(port=None, log_callback=log_esp32_communication)
    
    # Try to auto-detect ESP32 port dynamically
    detected_port = esp32_serial._auto_detect_port()
    if detected_port:
        esp32_serial.set_port(detected_port)
        print(f"📡 ESP32 dynamically detected on port: {detected_port}")
    else:
        # Only if absolutely no ESP32 found, use platform defaults
        if platform.system() == "Windows":
            default_port = "COM3"
        else:
            default_port = "/dev/ttyUSB0"
        
        esp32_serial.set_port(default_port)
        print(f"📡 No ESP32 detected, using fallback port: {default_port}")
        print("   Use the web interface to manually scan and connect")
except ImportError as e:
    print(f"⚠️ ESP32 serial module not available: {e}")
except Exception as e:
    print(f"⚠️ ESP32 serial initialization error: {e}")

# In-memory storage for ESP32 devices and commands (WiFi mode)
esp32_devices = {}
network_devices = {}  # WiFi connected ESP32 devices (alternative name)
pending_commands = {}
command_history = []

# Device management
active_device = None  # Currently selected device for commands
device_priority = ["serial", "wifi"]  # Default priority order

@app.route('/')
def index():
    """Serve the main vending machine interface"""
    return render_template('index.html')

@app.route('/vend/<int:slot_id>', methods=['POST'])
def vend(slot_id):
    """Handle vending requests for specific slots - supports device selection"""
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
        device_used = None
        
        # Use active device if selected
        if active_device:
            if active_device.startswith("serial_") and esp32_serial and esp32_serial.is_connected:
                # Use selected serial device
                success = esp32_serial.send_vend_command(slot_id)
                if success:
                    communication_used = "serial"
                    device_used = active_device
                    print(f"📡 Serial command sent to selected device {active_device}: VEND:{slot_id}")
                    
                    return jsonify({
                        "status": "command_sent",
                        "slot": slot_id,
                        "message": f"Command sent to selected ESP32 for slot {slot_id}",
                        "communication": "serial",
                        "device": active_device,
                        "device_port": esp32_serial.port
                    }), 200
                    
            elif active_device in esp32_devices and esp32_devices[active_device].get('status') == 'online':
                # Use selected WiFi device
                pending_commands[active_device] = {
                    "command": "VEND",
                    "slot": slot_id,
                    "timestamp": time.time()
                }
                
                communication_used = "wifi"
                device_used = active_device
                success = True
                print(f"📡 WiFi command queued for selected device {active_device}: Slot {slot_id}")
                
                # Log command
                log_esp32_communication("sent", f"VEND:{slot_id}", "command", 
                                      device_id=active_device, device_type="wifi")
                
                command_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "device_id": active_device,
                    "slot": slot_id,
                    "status": "sent",
                    "communication": "wifi"
                })
                
                return jsonify({
                    "status": "command_sent",
                    "slot": slot_id,
                    "message": f"Command sent to selected ESP32 for slot {slot_id}",
                    "device_id": active_device,
                    "communication": "wifi"
                }), 200
        
        # Fallback: Auto-select best available device
        # Priority 1: Try serial communication first (ESP32 via USB)
        if esp32_serial and esp32_serial.is_connected:
            success = esp32_serial.send_vend_command(slot_id)
            if success:
                communication_used = "serial"
                device_used = f"serial_{esp32_serial.port}"
                print(f"📡 Serial command sent to ESP32: VEND:{slot_id}")
                
                return jsonify({
                    "status": "command_sent",
                    "slot": slot_id,
                    "message": f"Serial command sent to ESP32 for slot {slot_id}",
                    "communication": "serial",
                    "device": device_used,
                    "device_port": esp32_serial.port
                }), 200
        
        # Priority 2: Check if any WiFi ESP32 devices are connected
        online_wifi_devices = get_online_wifi_devices()
        
        if online_wifi_devices:
            # Send command to first available ESP32 (WiFi mode)
            device_id = online_wifi_devices[0]
            
            # Store command for ESP32 to pick up
            pending_commands[device_id] = {
                "command": "VEND",
                "slot": slot_id,
                "timestamp": time.time()
            }
            
            communication_used = "wifi"
            device_used = device_id
            success = True
            print(f"📡 WiFi command queued for ESP32 {device_id}: Slot {slot_id}")
            
            # Log command
            log_esp32_communication("sent", f"VEND:{slot_id}", "command", 
                                  device_id=device_id, device_type="wifi")
            
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
    online_wifi_devices = get_online_wifi_devices()
    wifi_devices = len(online_wifi_devices)
    
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
            "wifi": f"{wifi_devices} devices online",
            "wifi_device_list": online_wifi_devices
        }
    })

# =================================
# ESP32 WiFi Communication Endpoints
# =================================

@app.route('/esp32/register', methods=['POST'])
def esp32_register():
    """Register a WiFi ESP32 device"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        ip_address = data.get('ip_address')
        
        if not device_id or not ip_address:
            return jsonify({"success": False, "error": "Missing device_id or ip_address"}), 400
        
        # Add to both storage systems for compatibility
        device_info = {
            "ip_address": ip_address,
            "last_seen": time.time(),
            "status": "online",  # Changed from "connected" to "online" for consistency
            "device_id": device_id,
            "type": "wifi"
        }
        
        # Store in both locations
        network_devices[device_id] = device_info
        esp32_devices[device_id] = device_info
        
        log_esp32_communication("received", f"WiFi device {device_id} registered from {ip_address}", 
                              "discovery", device_id, "wifi")
        
        print(f"📶 WiFi ESP32 registered: {device_id} from {ip_address}")
        
        return jsonify({"success": True, "message": f"Device {device_id} registered"})
        
    except Exception as e:
        log_esp32_communication("received", f"Registration error: {str(e)}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/esp32/connect', methods=['POST'])
def esp32_connect():
    """Alternative endpoint for ESP32 device connection"""
    return esp32_register()

@app.route('/esp32/data', methods=['POST'])
def esp32_data():
    """Receive data from ESP32 devices"""
    try:
        data = request.get_json()
        device_id = data.get('device_id', 'unknown')
        data_type = data.get('type', 'unknown')
        
        # Update last seen time for both storage systems
        current_time = time.time()
        
        if device_id in network_devices:
            network_devices[device_id]['last_seen'] = current_time
            network_devices[device_id]['status'] = 'online'
        
        if device_id in esp32_devices:
            esp32_devices[device_id]['last_seen'] = current_time
            esp32_devices[device_id]['status'] = 'online'
        else:
            # Add device if not exists
            esp32_devices[device_id] = {
                "ip_address": data.get('ip_address', 'unknown'),
                "last_seen": current_time,
                "status": "online",
                "device_id": device_id,
                "type": "wifi"
            }
        
        # Log the received data
        log_esp32_communication("received", f"Received {data_type} data: {data}", 
                              "info", device_id, "wifi")
        
        return jsonify({"success": True, "message": "Data received"})
        
    except Exception as e:
        log_esp32_communication("received", f"Data reception error: {str(e)}", "error")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/vend', methods=['POST'])
def vend_by_slot_name():
    """Vend by slot name (e.g., A1, B2, C3)"""
    try:
        data = request.get_json()
        slot_name = data.get('slot')
        
        if not slot_name:
            return jsonify({"success": False, "error": "Missing slot parameter"}), 400
        
        # Map slot names to IDs (simplified mapping)
        slot_mapping = {
            'A1': 1, 'A2': 2, 'A3': 3,
            'B1': 4, 'B2': 5, 'B3': 6,
            'C1': 7, 'C2': 8, 'C3': 9
        }
        
        slot_id = slot_mapping.get(slot_name)
        if not slot_id:
            return jsonify({"success": False, "error": f"Invalid slot name: {slot_name}"}), 400
        
        log_esp32_communication(f"Vending request for slot {slot_name} (ID: {slot_id})", 
                              "OUT", "system", "web")
        
        # Use existing vend function
        return vend(slot_id)
        
    except Exception as e:
        log_esp32_communication(f"Vending error: {str(e)}", "ERROR")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/esp32/commands/<device_id>', methods=['GET'])
def esp32_get_commands(device_id):
    """ESP32 polls for pending commands (WiFi mode)"""
    try:
        # Update last seen time for both storage systems
        current_time = time.time()
        
        if device_id in esp32_devices:
            esp32_devices[device_id]['last_seen'] = current_time
            esp32_devices[device_id]['status'] = 'online'
            
        if device_id in network_devices:
            network_devices[device_id]['last_seen'] = current_time
            network_devices[device_id]['status'] = 'online'
        else:
            # Add device if polling but not registered yet
            network_devices[device_id] = {
                "ip_address": request.remote_addr,
                "last_seen": current_time,
                "status": "online",
                "device_id": device_id,
                "type": "wifi"
            }
            esp32_devices[device_id] = network_devices[device_id]
        
        # Check for pending commands
        if device_id in pending_commands:
            command = pending_commands.pop(device_id)  # Remove after sending
            
            # Log the command being sent to WiFi device
            command_str = f"{command.get('command')}:{command.get('slot')}" if command.get('slot') else command.get('command')
            log_esp32_communication("sent", command_str, "command", 
                                  device_id=device_id, device_type="wifi")
            
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
        
        # Log the confirmation from WiFi device
        msg_type = "success" if success else "error"
        log_esp32_communication("received", message, msg_type, 
                              device_id=device_id, device_type="wifi")
        
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

# =================================
# ESP32 Connection Management
# =================================

@app.route('/esp32/serial/scan', methods=['GET'])
def esp32_serial_scan():
    """Scan for available serial ports"""
    if not esp32_serial:
        return jsonify({"error": "Serial communication not available"}), 500
    
    try:
        ports = esp32_serial.scan_ports()
        return jsonify({
            "status": "success",
            "ports": ports
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/esp32/serial/connect', methods=['POST'])
def esp32_serial_connect():
    """Connect to ESP32 via serial on specified port"""
    if not esp32_serial:
        return jsonify({"error": "Serial communication not available"}), 500
    
    try:
        data = request.get_json()
        port = data.get('port')
        
        if not port:
            return jsonify({"error": "Port required"}), 400
        
        # Attempt connection
        success = esp32_serial.connect(port)
        
        if success:
            return jsonify({
                "status": "connected",
                "port": port,
                "message": f"Successfully connected to ESP32 on {port}"
            }), 200
        else:
            # Check if it's a permission error (port in use)
            try:
                import serial
                test_serial = serial.Serial(port, 115200, timeout=0.5)
                test_serial.close()
                error_msg = f"ESP32 not responding on {port}. Check firmware."
            except PermissionError:
                error_msg = f"Port {port} is in use. Close Arduino IDE Serial Monitor or other serial programs."
            except Exception as e:
                error_msg = f"Cannot access {port}. Check connection and drivers."
            
            return jsonify({
                "status": "failed",
                "port": port,
                "message": error_msg
            }), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/esp32/serial/disconnect', methods=['POST'])
def esp32_serial_disconnect():
    """Disconnect ESP32 serial connection"""
    if not esp32_serial:
        return jsonify({"error": "Serial communication not available"}), 500
    
    try:
        esp32_serial.disconnect()
        return jsonify({
            "status": "disconnected",
            "message": "ESP32 serial connection closed"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/esp32/serial/status', methods=['GET'])
def esp32_serial_status():
    """Get detailed ESP32 serial status"""
    if not esp32_serial:
        return jsonify({"error": "Serial communication not available"}), 500
    
    return jsonify({
        "connected": esp32_serial.is_connected,
        "port": esp32_serial.port,
        "auto_reconnect": esp32_serial.auto_reconnect,
        "has_connection": esp32_serial.serial_connection is not None,
        "connection_open": esp32_serial.serial_connection.is_open if esp32_serial.serial_connection else False
    }), 200

@app.route('/esp32/communication/mode', methods=['GET', 'POST'])
def communication_mode():
    """Get or set preferred communication mode"""
    if request.method == 'GET':
        # Determine current active mode based on available devices
        mode = "none"
        serial_available = esp32_serial is not None and esp32_serial.is_connected
        wifi_devices = get_online_wifi_devices()
        
        if serial_available:
            mode = "serial"
        elif len(wifi_devices) > 0:
            mode = "wifi"
        
        return jsonify({
            "current_mode": mode,
            "serial_available": serial_available,
            "wifi_devices": len(wifi_devices),
            "wifi_device_list": wifi_devices,
            "modes": ["serial", "wifi", "simulation"],
            "active_device": active_device
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        preferred_mode = data.get('mode')
        
        if preferred_mode not in ['serial', 'wifi', 'simulation']:
            return jsonify({"error": "Invalid mode. Must be 'serial', 'wifi', or 'simulation'"}), 400
        
        # Note: This is informational - actual mode switching happens automatically based on availability
        return jsonify({
            "preferred_mode": preferred_mode,
            "message": f"Preferred mode set to {preferred_mode}. Actual mode depends on device availability."
        }), 200

def get_online_wifi_devices():
    """Get list of online WiFi devices from both storage systems"""
    online_devices = []
    current_time = time.time()
    
    # Check esp32_devices
    for device_id, device_info in esp32_devices.items():
        if device_info.get('status') == 'online':
            # Check if device is still active (last seen within 30 seconds)
            last_seen = device_info.get('last_seen', 0)
            if current_time - last_seen < 30:
                online_devices.append(device_id)
            else:
                # Mark as offline if too much time has passed
                device_info['status'] = 'offline'
    
    # Check network_devices as well
    for device_id, device_info in network_devices.items():
        if device_id not in online_devices and device_info.get('status') == 'online':
            last_seen = device_info.get('last_seen', 0)
            if current_time - last_seen < 30:
                online_devices.append(device_id)
            else:
                device_info['status'] = 'offline'
    
    return online_devices

# =================================
# Device Management Endpoints
# =================================

@app.route('/esp32/devices/list')
def list_all_devices():
    """List all available ESP32 devices (serial + WiFi)"""
    devices = []
    
    # Add serial device if available
    if esp32_serial:
        serial_device = {
            "device_id": f"serial_{esp32_serial.port}",
            "type": "serial",
            "port": esp32_serial.port,
            "connected": esp32_serial.is_connected,
            "status": "connected" if esp32_serial.is_connected else "disconnected",
            "info": getattr(esp32_serial, 'device_info', {})
        }
        devices.append(serial_device)
    
    # Add WiFi devices from both storage locations
    for device_id, device_info in esp32_devices.items():
        wifi_device = {
            "device_id": device_id,
            "type": "wifi",
            "ip_address": device_info.get('ip_address'),
            "connected": device_info.get('status') == 'online',
            "status": device_info.get('status', 'unknown'),
            "last_seen": device_info.get('last_seen'),
            "info": device_info
        }
        devices.append(wifi_device)
    
    # Add network devices (alternative storage)
    for device_id, device_info in network_devices.items():
        # Check if device already added from esp32_devices
        if not any(d['device_id'] == device_id for d in devices):
            wifi_device = {
                "device_id": device_id,
                "type": "wifi",
                "ip_address": device_info.get('ip_address'),
                "connected": device_info.get('status') == 'connected',
                "status": device_info.get('status', 'unknown'),
                "last_seen": device_info.get('last_seen'),
                "info": device_info
            }
            devices.append(wifi_device)
    
    return jsonify({
        "devices": devices,
        "active_device": active_device,
        "total_devices": len(devices),
        "connected_devices": len([d for d in devices if d['connected']])
    })

@app.route('/esp32/devices/select', methods=['POST'])
def select_active_device():
    """Select which device to use for commands"""
    global active_device
    
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({"error": "device_id required"}), 400
        
        # Validate device exists and is connected
        device_exists = False
        device_connected = False
        device_type = "unknown"
        
        # Check serial device
        if esp32_serial and device_id == f"serial_{esp32_serial.port}":
            device_exists = True
            device_connected = esp32_serial.is_connected
            device_type = "serial"
        
        # Check WiFi devices in both storage locations
        elif device_id in esp32_devices:
            device_exists = True
            device_connected = esp32_devices[device_id].get('status') == 'online'
            device_type = "wifi"
        elif device_id in network_devices:
            device_exists = True
            device_connected = network_devices[device_id].get('status') == 'online'
            device_type = "wifi"
        
        if not device_exists:
            return jsonify({"error": "Device not found"}), 404
        
        if not device_connected:
            return jsonify({
                "error": f"Device {device_id} is not connected", 
                "device_type": device_type,
                "status": "offline"
            }), 400
        
        active_device = device_id
        
        print(f"🎯 Active device selected: {device_id} ({device_type})")
        
        return jsonify({
            "active_device": active_device,
            "device_type": device_type,
            "message": f"Active device set to {device_id}",
            "status": "online"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/esp32/devices/auto-select', methods=['POST'])
def auto_select_device():
    """Auto-select best available device based on priority"""
    global active_device
    
    try:
        # Priority: Serial first, then WiFi
        selected_device = None
        device_type = None
        
        # Check serial device first
        if esp32_serial and esp32_serial.is_connected:
            selected_device = f"serial_{esp32_serial.port}"
            device_type = "serial"
            print(f"🎯 Auto-selected serial device: {selected_device}")
        
        # Check WiFi devices if no serial
        if not selected_device:
            online_wifi = get_online_wifi_devices()
            if online_wifi:
                selected_device = online_wifi[0]  # Use first available WiFi device
                device_type = "wifi"
                print(f"🎯 Auto-selected WiFi device: {selected_device}")
        
        if selected_device:
            active_device = selected_device
            return jsonify({
                "active_device": active_device,
                "device_type": device_type,
                "message": f"Auto-selected {device_type} device: {active_device}",
                "status": "online"
            }), 200
        else:
            active_device = None
            return jsonify({
                "active_device": None,
                "device_type": None,
                "message": "No connected devices available for auto-selection",
                "status": "none"
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/esp32/communication/log')
def communication_log():
    """Get recent ESP32 communication log"""
    return jsonify({
        "log_entries": esp32_comm_log[-50:],  # Last 50 entries
        "total_entries": len(esp32_comm_log)
    })

@app.route('/esp32/communication/log/clear', methods=['POST'])
def clear_communication_log():
    """Clear the communication log"""
    global esp32_comm_log
    esp32_comm_log = []
    return jsonify({"message": "Communication log cleared"})

@app.route('/esp32/communication/test', methods=['POST'])
def test_communication_log():
    """Add test entries to communication log for testing"""
    test_entries = [
        ("sent", "DISCOVER", "command"),
        ("received", "ESP32_USB_VENDING v1.1", "discovery"),
        ("sent", "STATUS", "command"),
        ("received", "STATUS:READY,SLOTS:5,FIRMWARE:1.1", "status"),
        ("sent", "VEND:1", "command"),
        ("received", "VEND:1:SUCCESS", "vend"),
        ("received", "SLOT_1_DISPENSED", "success")
    ]
    
    for direction, message, msg_type in test_entries:
        log_esp32_communication(direction, message, msg_type)
    
    return jsonify({
        "message": "Test communication log entries added",
        "entries_added": len(test_entries)
    })

def start_udp_discovery_service():
    """Start UDP service for ESP32 auto-discovery"""
    import socket
    import threading
    
    def udp_discovery_handler():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.bind(('', 12346))
            sock.settimeout(1.0)  # Non-blocking with timeout
            
            print("📻 UDP discovery service started on port 12346")
            
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = data.decode()
                    
                    if message == "ESP32_DISCOVERY_REQUEST":
                        # Get local IP address
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect(("8.8.8.8", 80))
                        local_ip = s.getsockname()[0]
                        s.close()
                        
                        # Send response with Flask server IP
                        response = f"FLASK_SERVER:{local_ip}"
                        sock.sendto(response.encode(), addr)
                        print(f"📡 Sent discovery response to {addr[0]}: {local_ip}")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"⚠️ UDP discovery error: {e}")
                    break
                    
        except Exception as e:
            print(f"⚠️ Failed to start UDP discovery: {e}")
    
    # Start UDP discovery in background thread
    threading.Thread(target=udp_discovery_handler, daemon=True).start()

if __name__ == '__main__':
    print("🏪 Flask Vending Machine Server (Hybrid Communication)")
    print("=" * 60)
    
    # Start UDP discovery service for fast ESP32 detection
    start_udp_discovery_service()
    
    # Try to connect to ESP32 via serial
    if esp32_serial:
        print("🔌 Attempting to connect to ESP32 via USB serial...")
        if esp32_serial.connect():
            print(f"✅ ESP32 connected via serial (USB port: {esp32_serial.port})")
        else:
            print("❌ ESP32 not found on serial port")
            print("   Make sure ESP32 is connected via USB")
            print("   You can manually connect through the web interface")
            print("   Use the Connection Management panel at http://localhost:5000")
    
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
        # Disable debug mode to prevent auto-restart that interferes with serial connections
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        if esp32_serial and esp32_serial.is_connected:
            esp32_serial.disconnect()
            print("🔌 ESP32 serial connection closed")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        if esp32_serial and esp32_serial.is_connected:
            esp32_serial.disconnect()