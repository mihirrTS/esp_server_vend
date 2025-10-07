"""
Flask Serial Communication Module
Enhanced with auto-discovery and fast communication
"""

import serial
import serial.tools.list_ports
import threading
import time
import platform
from queue import Queue

class ESP32SerialCommunication:
    def __init__(self, port=None, baudrate=115200, log_callback=None):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.command_queue = Queue()
        self.response_queue = Queue()
        self.is_connected = False
        self.auto_reconnect = True
        self.connection_monitor_thread = None
        self.log_callback = log_callback  # Callback for logging communication
        self.device_id = None  # Will be set when connected
        self.device_info = {}  # Store device information
        
    def set_port(self, port):
        """Manually set the port"""
        self.port = port
        
    def scan_ports(self):
        """Scan and return available serial ports with enhanced ESP32 detection"""
        print("🔍 Scanning for serial ports...")
        ports = serial.tools.list_ports.comports()
        available_ports = []
        
        for port in ports:
            port_info = {
                'device': port.device,
                'description': port.description or "Unknown device",
                'hwid': port.hwid or "",
                'likely_esp32': self._is_likely_esp32_dynamic(port),
                'available': True,
                'status': 'available',
                'esp32_confidence': 'unknown'
            }
            
            # Test if port is available (not in use)
            try:
                test_serial = serial.Serial(port.device, self.baudrate, timeout=0.5)
                test_serial.close()
                port_info['status'] = 'available'
                
                # If available, test for ESP32 communication
                if self._test_esp32_communication(port.device):
                    port_info['esp32_confidence'] = 'high'
                    port_info['likely_esp32'] = True
                elif self._is_likely_esp32_dynamic(port):
                    port_info['esp32_confidence'] = 'medium'
                else:
                    port_info['esp32_confidence'] = 'low'
                    
            except PermissionError:
                port_info['available'] = False
                port_info['status'] = 'in_use'
            except Exception:
                port_info['available'] = False
                port_info['status'] = 'error'
            
            available_ports.append(port_info)
            
            # Enhanced port display
            status_icon = "🟢" if port_info['available'] else "🔴"
            esp32_icon = "⭐" if port_info['likely_esp32'] else "  "
            usage_text = ""
            if not port_info['available']:
                usage_text = " (in use)" if port_info['status'] == 'in_use' else " (error)"
            
            print(f"{status_icon} {esp32_icon} {port.device} - {port.description}{usage_text}")
            
        return available_ports
    
    def _is_likely_esp32(self, port):
        """Check if port is likely an ESP32 (legacy method)"""
        return self._is_likely_esp32_dynamic(port)
    
    def _is_likely_esp32_dynamic(self, port):
        """Dynamically check if port is likely an ESP32"""
        description = (port.description or "").lower()
        hwid = (port.hwid or "").lower()
        
        # Skip known non-ESP32 devices
        non_esp32_indicators = ['samsung', 'modem', 'bluetooth', 'virtual', 'com0com']
        if any(indicator in description for indicator in non_esp32_indicators):
            return False
        
        # Check for ESP32 hardware indicators
        esp32_indicators = [
            'cp210x', 'ch340', 'esp32', 'usb-serial', 'cp2102', 'ch9102', 
            'ft232', 'pl2303', 'arduino', 'usb2.0-serial'
        ]
        
        # Check description
        if any(indicator in description for indicator in esp32_indicators):
            return True
        
        # Check hardware ID
        if any(indicator in hwid for indicator in esp32_indicators):
            return True
        
        return False
        
    def _auto_detect_port(self):
        """Auto-detect ESP32 serial port dynamically"""
        print("🔍 Auto-detecting ESP32 serial port...")
        
        # Get list of available ports
        ports = serial.tools.list_ports.comports()
        
        # First pass: Look for ports with ESP32-like hardware descriptions
        esp32_candidates = []
        
        for port in ports:
            port_name = port.device
            description = port.description or ""
            hwid = port.hwid or ""
            
            print(f"📍 Found port: {port_name} - {description}")
            
            # Skip known non-ESP32 devices
            description_lower = description.lower()
            if any(skip_term in description_lower for skip_term in [
                'samsung', 'modem', 'bluetooth', 'virtual', 'com0com'
            ]):
                print(f"⚠️ Skipping {port_name} - {description} (not ESP32)")
                continue
            
            # Check for ESP32 hardware indicators
            esp32_indicators = ['ch340', 'cp210x', 'ch9102', 'esp32', 'usb-serial', 'cp2102', 'ft232']
            if any(indicator in description_lower for indicator in esp32_indicators):
                esp32_candidates.append((port_name, description, "hardware_match"))
                print(f"🎯 ESP32 candidate found: {port_name} - {description}")
        
        # Second pass: Test candidates for actual ESP32 communication
        for port_name, description, reason in esp32_candidates:
            print(f"🧪 Testing ESP32 communication on {port_name}...")
            if self._test_esp32_communication(port_name):
                print(f"✅ Confirmed ESP32 on: {port_name}")
                return port_name
        
        # Third pass: If no hardware matches, test all remaining ports
        print("� No hardware matches found, testing all available ports...")
        for port in ports:
            port_name = port.device
            description = (port.description or "").lower()
            
            # Skip already tested candidates and known non-ESP32 devices
            if any(candidate[0] == port_name for candidate in esp32_candidates):
                continue
            if any(skip_term in description for skip_term in [
                'samsung', 'modem', 'bluetooth', 'virtual', 'com0com'
            ]):
                continue
            
            print(f"🧪 Testing communication on {port_name}...")
            if self._test_esp32_communication(port_name):
                print(f"✅ Found ESP32 on: {port_name}")
                return port_name
        
        print("❌ No ESP32 devices found on any port")
        return None
    
    def _test_esp32_communication(self, port):
        """Test if a port has ESP32-like communication"""
        try:
            # Check if port exists
            ports = [p.device for p in serial.tools.list_ports.comports()]
            if port not in ports:
                return False
            
            test_serial = serial.Serial(port, self.baudrate, timeout=2)
            time.sleep(0.3)  # Brief initialization time
            
            # Clear buffers
            test_serial.reset_input_buffer()
            test_serial.reset_output_buffer()
            
            # Send a simple test command
            test_serial.write(b"AT\n")
            test_serial.flush()
            time.sleep(0.5)
            
            response_data = None
            if test_serial.in_waiting > 0:
                response_data = test_serial.read(test_serial.in_waiting)
                print(f"📡 Response from {port}: {response_data}")
            
            test_serial.close()
            
            if response_data:
                try:
                    response_str = response_data.decode('utf-8', errors='ignore')
                    
                    # ESP32-like responses (error messages, help, commands)
                    esp32_indicators = ['error', 'help', 'command', 'unknown', 'esp32', 'ready', 'ok']
                    if any(indicator in response_str.lower() for indicator in esp32_indicators):
                        return True
                    
                    # Check for formatted responses (ESP32s often format output)
                    if any(char in response_str for char in ['📨', '❌', '💡', '🔧']) or \
                       'Type' in response_str or 'available' in response_str.lower():
                        return True
                    
                    # If it just echoes the command, likely a modem
                    if response_str.strip() == "AT":
                        print(f"⚠️ {port} echoed command - likely modem")
                        return False
                        
                except:
                    # Binary or malformed response might still be ESP32
                    pass
                
                return True  # Any response could be ESP32
            
            # No response - check hardware description as fallback
            for test_port in serial.tools.list_ports.comports():
                if test_port.device == port:
                    description = (test_port.description or "").lower()
                    if any(indicator in description for indicator in ['ch340', 'cp210x', 'ch9102', 'esp32']):
                        print(f"✅ No response but hardware suggests ESP32: {test_port.description}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error testing {port}: {e}")
            return False
    
    def _test_esp32_port(self, port):
        """Legacy method - now uses the new communication test"""
        return self._test_esp32_communication(port)
        
    def connect(self, port=None):
        """Connect to ESP32 with improved error handling and monitoring"""
        if port:
            self.port = port
            
        if not self.port:
            print("❌ No port specified. Use scan_ports() to find available ports.")
            return False
            
        print(f"🔌 Attempting to connect to ESP32 on {self.port}...")
        
        # Disconnect if already connected
        if self.is_connected:
            self.disconnect()
            
        try:
            # Optimized serial settings with better error handling
            self.serial_connection = serial.Serial(
                port=self.port, 
                baudrate=self.baudrate, 
                timeout=1.0,  # Increased for better detection
                write_timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(2)  # Give ESP32 time to respond
            
            # Verify it's our ESP32 vending machine
            if self._verify_esp32_device():
                self.is_connected = True
                
                # Set device ID for logging
                self.device_id = f"serial_{self.port}"
                self.device_info = {
                    "device_id": self.device_id,
                    "type": "serial",
                    "port": self.port,
                    "baudrate": self.baudrate,
                    "status": "connected"
                }
                
                # Start communication handler
                threading.Thread(target=self._serial_handler, daemon=True).start()
                
                # Start connection monitor
                if self.auto_reconnect:
                    self.connection_monitor_thread = threading.Thread(target=self._connection_monitor, daemon=True)
                    self.connection_monitor_thread.start()
                
                print(f"✅ Connected to ESP32 vending machine on {self.port}")
                return True
            else:
                print(f"⚠️ Device on {self.port} is not responding as ESP32 vending machine")
                if self.serial_connection:
                    self.serial_connection.close()
                return False
                
        except PermissionError:
            print(f"❌ Permission denied for {self.port}")
            print("   • Port is already in use by another application")
            print("   • Close Arduino IDE Serial Monitor or other serial programs")
            print("   • Try a different port or restart the application using the port")
            self.is_connected = False
            return False
        except FileNotFoundError:
            print(f"❌ Port {self.port} not found")
            print("   • Check if ESP32 is properly connected")
            print("   • Verify the correct port number")
            print("   • Try scanning for available ports")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"❌ Failed to connect to ESP32 on {self.port}: {e}")
            self.is_connected = False
            return False
    
    def _connection_monitor(self):
        """Monitor connection and update status"""
        while self.auto_reconnect and self.is_connected:
            try:
                if self.serial_connection and not self.serial_connection.is_open:
                    print("⚠️ Serial connection lost, marking as disconnected")
                    self.is_connected = False
                    break
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"⚠️ Connection monitor error: {e}")
                self.is_connected = False
                break
    
    def _verify_esp32_device(self):
        """Verify the connected device is an ESP32 (more lenient check)"""
        try:
            # Clear any existing data in buffer
            self.serial_connection.reset_input_buffer()
            time.sleep(0.1)
            
            # Send simple AT command (most ESP32s respond to this)
            self.serial_connection.write(b"AT\n")
            self.serial_connection.flush()
            
            # Wait for any response
            start_time = time.time()
            responses = []
            
            while time.time() - start_time < 3:  # 3 second timeout
                if self.serial_connection.in_waiting:
                    try:
                        response = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                        if response:
                            responses.append(response)
                            print(f"📡 Received: {response}")
                    except:
                        # Handle any decoding errors
                        raw_response = self.serial_connection.readline()
                        responses.append(f"[Raw: {raw_response}]")
                        print(f"📡 Received raw: {raw_response}")
                
                time.sleep(0.1)
            
            # If we got any response, consider it a valid ESP32
            if responses:
                print(f"✅ ESP32 device detected (responses: {len(responses)})")
                return True
            
            # Even if no response, if port was detected as ESP32 hardware, allow connection
            # This handles cases where ESP32 is in deep sleep or running custom firmware
            for test_port in serial.tools.list_ports.comports():
                if test_port.device == self.port:
                    description = (test_port.description or "").lower()
                    if any(indicator in description for indicator in ['ch340', 'cp210x', 'ch9102', 'esp32']):
                        print(f"✅ ESP32 hardware detected by port description: {test_port.description}")
                        return True
            
            print(f"⚠️ No ESP32 response detected. Responses: {responses}")
            # Still allow connection for manual override
            return True  # Changed to always return True for manual connection
            
        except Exception as e:
            print(f"⚠️ Device verification error: {e}")
            # Allow connection even if verification fails
            return True
    
    def send_vend_command(self, slot_id):
        """Send vend command to ESP32"""
        if self.is_connected:
            command = f"VEND:{slot_id}\n"
            self.command_queue.put(command)
            print(f"📤 Queued command: {command.strip()}")
            return True
        else:
            print(f"❌ Not connected to ESP32")
            return False
    
    def send_command(self, command, wait_for_response=True, timeout=5):
        """Send any command to ESP32 and optionally wait for response"""
        if not self.is_connected or not self.serial_connection or not self.serial_connection.is_open:
            print("❌ ESP32 not connected")
            return None
        
        try:
            # Add newline if not present
            if not command.endswith('\n'):
                command += '\n'
                
            self.command_queue.put(command)
            
            if wait_for_response:
                try:
                    # Wait for response
                    response = self.response_queue.get(timeout=timeout)
                    return response
                except:
                    print(f"⏰ Timeout waiting for response to: {command.strip()}")
                    return None
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending command '{command.strip()}': {e}")
            self.is_connected = False
            return None
    
    def get_status(self):
        """Get ESP32 status"""
        return self.send_command("STATUS", wait_for_response=True, timeout=3)
    
    def _serial_handler(self):
        """Background thread to handle serial communication with enhanced logging"""
        while self.is_connected:
            try:
                # Send queued commands with immediate processing
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self.serial_connection.write(command.encode())
                    self.serial_connection.flush()  # Force immediate send
                    print(f"📡 [SENT] {command.strip()}")
                    
                    # Log to callback if available
                    if self.log_callback:
                        self.log_callback("sent", command.strip(), "command", 
                                        device_id=self.device_id, device_type="serial")
                
                # Read responses with faster polling and detailed logging
                if self.serial_connection.in_waiting:
                    response = self.serial_connection.readline().decode().strip()
                    if response:
                        print(f"📨 [RECV] {response}")
                        
                        # Determine message type for logging
                        response_upper = response.upper()
                        msg_type = "info"
                        if "VEND" in response_upper:
                            print(f"🏪 [VEND] Vending response: {response}")
                            msg_type = "vend"
                        elif "STATUS" in response_upper:
                            print(f"📊 [STATUS] Device status: {response}")
                            msg_type = "status"
                        elif "DISCOVER" in response_upper or "ESP32" in response_upper:
                            print(f"🔍 [DISCOVERY] Device info: {response}")
                            msg_type = "discovery"
                        elif "ERROR" in response_upper:
                            print(f"❌ [ERROR] ESP32 error: {response}")
                            msg_type = "error"
                        elif "SUCCESS" in response_upper or "OK" in response_upper:
                            print(f"✅ [SUCCESS] Command completed: {response}")
                            msg_type = "success"
                        else:
                            print(f"💬 [INFO] ESP32 message: {response}")
                            msg_type = "info"
                        
                        # Log to callback if available
                        if self.log_callback:
                            self.log_callback("received", response, msg_type,
                                            device_id=self.device_id, device_type="serial")
                            
                        self.response_queue.put(response)
                
                time.sleep(0.05)  # Faster polling for better responsiveness
                
            except Exception as e:
                print(f"❌ [ERROR] Serial communication error: {e}")
                if self.log_callback:
                    self.log_callback("error", f"Serial communication error: {e}", "error")
                self.is_connected = False
                break
    
    def disconnect(self):
        """Properly disconnect from ESP32"""
        self.is_connected = False
        self.auto_reconnect = False
        
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                print("🔌 Disconnected from ESP32")
            except Exception as e:
                print(f"⚠️ Error during disconnect: {e}")
        
        # Clear queues
        while not self.command_queue.empty():
            self.command_queue.get()
        while not self.response_queue.empty():
            self.response_queue.get()
    
    def reconnect(self):
        """Attempt to reconnect"""
        print("🔄 Attempting to reconnect...")
        self.disconnect()
        time.sleep(1)
        return self.connect()

# Add this to your Flask app.py
"""
# At the top of app.py, add:
from esp32_serial import ESP32SerialCommunication

# Initialize serial communication
esp32_serial = ESP32SerialCommunication(port='COM3')  # Adjust port as needed

# In your Flask app startup:
if __name__ == '__main__':
    # Try to connect to ESP32
    esp32_serial.connect()
    
    print("Starting Flask Vending Machine Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)

# Update the vend() function:
@app.route('/vend/<int:slot_id>', methods=['POST'])
def vend(slot_id):
    # ... existing validation code ...
    
    # Try serial communication first
    if esp32_serial.is_connected:
        success = esp32_serial.send_vend_command(slot_id)
        if success:
            return jsonify({
                "status": "command_sent",
                "slot": slot_id,
                "message": f"Serial command sent to ESP32 for slot {slot_id}",
                "communication": "serial"
            }), 200
    
    # Fallback to simulation
    print(f"🖥️ Simulating: VEND:{slot_id}")
    return jsonify({
        "status": "command_sent",
        "slot": slot_id,
        "message": f"Simulated vend command for slot {slot_id}",
        "communication": "simulation"
    }), 200
"""