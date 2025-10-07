"""
Flask Serial Communication Module
Add this to app.py for USB/Serial communication with ESP32
"""

import serial
import threading
import time
from queue import Queue

class ESP32SerialCommunication:
    def __init__(self, port='COM3', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.command_queue = Queue()
        self.response_queue = Queue()
        self.is_connected = False
        
    def connect(self):
        """Connect to ESP32 via serial"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for connection to stabilize
            self.is_connected = True
            
            # Start background thread to handle serial communication
            threading.Thread(target=self._serial_handler, daemon=True).start()
            
            print(f"✅ Connected to ESP32 on {self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to ESP32: {e}")
            self.is_connected = False
            return False
    
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
    
    def _serial_handler(self):
        """Background thread to handle serial communication"""
        while self.is_connected:
            try:
                # Send queued commands
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self.serial_connection.write(command.encode())
                    print(f"📡 Sent to ESP32: {command.strip()}")
                
                # Read responses
                if self.serial_connection.in_waiting:
                    response = self.serial_connection.readline().decode().strip()
                    if response:
                        print(f"📨 ESP32 Response: {response}")
                        self.response_queue.put(response)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Serial communication error: {e}")
                self.is_connected = False
                break
    
    def disconnect(self):
        """Disconnect from ESP32"""
        self.is_connected = False
        if self.serial_connection:
            self.serial_connection.close()
        print("🔌 Disconnected from ESP32")

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