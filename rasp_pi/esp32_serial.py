"""
ESP32 Serial Communication for Raspberry Pi
Handles USB serial communication with ESP32 vending machine controller
"""

import serial
import threading
import time
from queue import Queue
import glob

class ESP32SerialCommunication:
    def __init__(self, port=None, baudrate=115200):
        self.port = port or self._auto_detect_port()
        self.baudrate = baudrate
        self.serial_connection = None
        self.command_queue = Queue()
        self.response_queue = Queue()
        self.is_connected = False
        self._stop_thread = False
        
    def _auto_detect_port(self):
        """Auto-detect ESP32 serial port on Raspberry Pi"""
        possible_ports = [
            '/dev/ttyUSB0',
            '/dev/ttyUSB1', 
            '/dev/ttyACM0',
            '/dev/ttyACM1',
            '/dev/serial0',  # Raspberry Pi GPIO serial
            '/dev/ttyAMA0'   # Raspberry Pi GPIO serial (older)
        ]
        
        # Also check for any USB serial devices
        usb_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        possible_ports.extend(usb_ports)
        
        print(f"🔍 Auto-detecting ESP32 port from: {possible_ports}")
        
        for port in possible_ports:
            try:
                # Try to open port briefly to test
                test_serial = serial.Serial(port, self.baudrate, timeout=0.5)
                test_serial.close()
                print(f"✅ Found available port: {port}")
                return port
            except (serial.SerialException, FileNotFoundError, PermissionError):
                continue
        
        print("❌ No ESP32 port auto-detected, using /dev/ttyUSB0 as default")
        return '/dev/ttyUSB0'
        
    def connect(self):
        """Connect to ESP32 via serial"""
        try:
            print(f"🔌 Connecting to ESP32 on {self.port} at {self.baudrate} baud...")
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            
            time.sleep(2)  # Wait for connection to stabilize
            
            # Clear any existing data
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            
            self.is_connected = True
            self._stop_thread = False
            
            # Start background thread to handle serial communication
            self.serial_thread = threading.Thread(target=self._serial_handler, daemon=True)
            self.serial_thread.start()
            
            # Test connection by sending STATUS command
            self.send_command("STATUS")
            
            print(f"✅ Connected to ESP32 on {self.port}")
            return True
            
        except serial.SerialException as e:
            print(f"❌ Serial connection failed: {e}")
            print("💡 Tips:")
            print("   - Check if ESP32 is connected via USB")
            print("   - Verify port permissions: sudo usermod -a -G dialout $USER")
            print("   - Try a different USB port")
            print("   - Make sure no other program is using the serial port")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"❌ Unexpected error connecting to ESP32: {e}")
            self.is_connected = False
            return False
    
    def send_vend_command(self, slot_id):
        """Send vend command to ESP32"""
        command = f"VEND:{slot_id}"
        return self.send_command(command)
    
    def send_command(self, command):
        """Send any command to ESP32"""
        if self.is_connected and self.serial_connection:
            try:
                self.command_queue.put(command)
                print(f"📤 Queued command: {command}")
                return True
            except Exception as e:
                print(f"❌ Error queuing command: {e}")
                return False
        else:
            print(f"❌ Cannot send command - ESP32 not connected")
            return False
    
    def _serial_handler(self):
        """Background thread to handle serial communication"""
        print("🔄 Serial handler thread started")
        
        while self.is_connected and not self._stop_thread:
            try:
                # Send queued commands
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    full_command = f"{command}\n"
                    self.serial_connection.write(full_command.encode('utf-8'))
                    print(f"📡 Sent to ESP32: {command}")
                
                # Read responses
                if self.serial_connection.in_waiting > 0:
                    try:
                        response = self.serial_connection.readline().decode('utf-8').strip()
                        if response:
                            print(f"📨 ESP32: {response}")
                            self.response_queue.put(response)
                    except UnicodeDecodeError as e:
                        print(f"⚠️ Decode error: {e}")
                
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
            except serial.SerialException as e:
                print(f"❌ Serial communication error: {e}")
                self.is_connected = False
                break
            except Exception as e:
                print(f"❌ Unexpected error in serial handler: {e}")
                break
        
        print("🔄 Serial handler thread stopped")
    
    def get_recent_responses(self, count=5):
        """Get recent responses from ESP32"""
        responses = []
        temp_responses = []
        
        # Get all responses from queue
        while not self.response_queue.empty():
            temp_responses.append(self.response_queue.get())
        
        # Return last 'count' responses
        return temp_responses[-count:] if temp_responses else []
    
    def disconnect(self):
        """Disconnect from ESP32"""
        print("🔌 Disconnecting from ESP32...")
        self._stop_thread = True
        self.is_connected = False
        
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                print("✅ ESP32 serial connection closed")
            except Exception as e:
                print(f"⚠️ Error closing serial connection: {e}")
        
        self.serial_connection = None
    
    def get_status(self):
        """Get connection status and info"""
        return {
            "connected": self.is_connected,
            "port": self.port,
            "baudrate": self.baudrate,
            "queue_size": self.command_queue.qsize(),
            "response_count": self.response_queue.qsize()
        }

# Test function for standalone testing
def test_esp32_serial():
    """Test ESP32 serial communication standalone"""
    print("🧪 Testing ESP32 Serial Communication")
    print("=" * 40)
    
    esp32 = ESP32SerialCommunication()
    
    if esp32.connect():
        print("✅ Connection successful!")
        
        # Test basic commands
        test_commands = ["STATUS", "VEND:1", "VEND:3", "HELP"]
        
        for command in test_commands:
            print(f"\n📤 Sending: {command}")
            esp32.send_command(command)
            time.sleep(2)  # Wait for response
            
            # Check responses
            responses = esp32.get_recent_responses()
            for response in responses:
                print(f"📨 Response: {response}")
        
        print("\n⏳ Waiting 5 seconds for any additional responses...")
        time.sleep(5)
        
        # Final response check
        final_responses = esp32.get_recent_responses()
        if final_responses:
            print("📨 Final responses:")
            for response in final_responses:
                print(f"   {response}")
        
        esp32.disconnect()
        print("✅ Test completed")
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    test_esp32_serial()