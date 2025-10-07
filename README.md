# Flask ESP32 Vending Machine System

A comprehensive vending machine control system with **multi-device ESP32 support** through both USB serial and WiFi connections, featuring **automatic IP discovery** for zero-configuration WiFi setup.

## 🌟 Key Features

### Multi-Device ESP32 Management
- **Automatic device detection** and connection management
- **USB Serial connection** for direct ESP32 communication
- **WiFi connection** support with **automatic Flask server discovery**
- **Zero-configuration WiFi setup** - no manual IP configuration required
- **Device switching** - seamlessly switch between multiple ESP32 devices
- **Priority-based selection** - Serial connections take priority over WiFi

### Automatic WiFi Discovery System
- **UDP broadcast discovery** - ESP32 automatically finds Flask server on the network
- **No manual IP configuration** - ESP32 discovers server IP automatically via UDP broadcast on port 12346
- **Dynamic server detection** - works across different networks and IP ranges
- **Automatic connection establishment** - ESP32 connects immediately upon discovery
- **Network-agnostic operation** - works on any local network configuration

### Enhanced Web Interface
- **Real-time status monitoring** of all connected devices
- **Interactive device selection** with visual status indicators
- **Live communication monitoring** to see ESP32 messages in real-time
- **Multi-connection support** - manage both serial and WiFi devices simultaneously
- **Automatic refresh cycles** - devices and status update automatically

### System Validation
- **Automated system check** script (`check_system.py`)
- **5-test validation suite** covering requirements, environment, hardware, Flask server, and connectivity
- **Detailed diagnostics** with specific recommendations for issues
- **End-to-end testing** including WiFi discovery validation

## 📁 Project Structure

```
flask-vending-machine/
├── src/                           # 💻 Main Flask application
│   ├── app.py                     # Flask server with hybrid communication
│   ├── templates/index.html       # Web interface
│   └── static/                    # CSS, JavaScript, assets
├── esp_code/                      # 🔌 ESP32 firmware
│   ├── esp32_mock_vend/           # USB serial firmware
│   └── esp32_wifi_vend/           # WiFi firmware
├── esp32_serial.py               # Python serial communication module
├── check_system.py               # 🧪 System test and validation script
├── setup.bat                      # 🚀 Windows setup script
├── start.bat                      # ▶️ Windows start server script
└── requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### Windows Setup:
```powershell
# Step 1: One-time setup (only run this once)
.\setup.bat

# Step 2: Start server (run this each time)
.\start.bat

# Step 3: Open web interface
# Browser will open automatically or go to: http://localhost:5000
```

### Linux/Raspberry Pi Setup:
```bash
# Step 1: Install Python and pip (if not already installed)
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Step 2: Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Step 3: Start server
python src/app.py

# Step 4: Open web interface
# Go to: http://localhost:5000 or http://[YOUR_PI_IP]:5000
```

## 🥧 Raspberry Pi Production Setup

For production deployment on Raspberry Pi OS:

### Quick Pi Setup:
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install required packages
sudo apt install python3 python3-pip python3-venv git -y

# 3. Clone and setup project
git clone <your-repo-url> flask-vending-machine
cd flask-vending-machine

# 4. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Add user to dialout group for serial access
sudo usermod -a -G dialout $USER

# 7. Test system
python check_system.py

# 8. Start server
python src/app.py
```

### Pi Auto-Start Service (Optional):
Create a systemd service to auto-start the vending machine:

```bash
# Create service file
sudo nano /etc/systemd/system/vending-machine.service
```

Add this content:
```ini
[Unit]
Description=Flask Vending Machine
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/flask-vending-machine
Environment=PATH=/home/pi/flask-vending-machine/venv/bin
ExecStart=/home/pi/flask-vending-machine/venv/bin/python src/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable vending-machine.service
sudo systemctl start vending-machine.service
sudo systemctl status vending-machine.service
```

### Pi Network Access:
```bash
# Find your Pi's IP address
hostname -I

# Access from other devices on the network:
# http://[PI_IP_ADDRESS]:5000
# Example: http://192.168.1.100:5000
```

## 🧪 Testing the System

Before starting the server, test your setup:

```bash
python check_system.py
```

### What the Test Checks:
- ✅ **System Requirements**: OS, Python version, required files
- ✅ **Python Environment**: Dependencies installation 
- ✅ **ESP32 Module**: Import and connection test
- ✅ **Flask Application**: Server functionality
- ✅ **Server Connection**: Live server status (if running)

### Expected Output:
```
============================================================
 Flask Vending Machine - System Check
============================================================
🧪 Running System Requirements test...
✅ Operating System: Linux
✅ Found: src/app.py
✅ Found: esp32_serial.py
✅ Found: requirements.txt
✅ All required files present

🧪 Running Python Environment test...
✅ Python version compatible
✅ flask: Flask web framework - Available
✅ serial: PySerial for ESP32 communication - Available
✅ requests: HTTP requests library - Available
```

## 🤖 ESP32 Communication Setup

### Choose Your Method:

| Method | Best For | Firmware | Range | Setup |
|--------|----------|----------|--------|--------|
| **🔌 USB Serial** | Development, Testing | `esp32_mock_vend.ino` | Cable length | Plug & play |
| **📡 WiFi Network** | Production, Multiple devices | `esp32_wifi_vend.ino` | WiFi range | Network config |
| **🖥️ Simulation** | Testing without hardware | None needed | N/A | Just run Flask |

### 🔌 Method 1: USB Serial (Recommended for Testing)

#### Step 1: Connect Hardware
1. Connect ESP32 to computer via USB cable
2. Install ESP32 drivers if needed (CP210x or CH340)

#### Step 2: Flash ESP32 Firmware
1. Open `esp_code/esp32_mock_vend/esp32_mock_vend.ino` in Arduino IDE
2. Select board: **ESP32 Dev Module**
3. Select correct port
4. Upload code

#### Step 3: Verify Connection
1. Open Serial Monitor (115200 baud)
2. Press ESP32 RESET button
3. Should see:
   ```
   ESP32 Mock Vending Machine v1.0
   System ready!
   Waiting for commands from Flask server...
   ```

### 📡 Method 2: WiFi Network with Auto-Discovery (Production)

#### Step 1: Configure WiFi Credentials (No IP Configuration Needed!)
Edit `esp_code/esp32_wifi_vend/esp32_wifi_vend.ino`:
```cpp
const char* WIFI_SSID = "YOUR_WIFI_NETWORK";      // Your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Your WiFi password
// NOTE: No FLASK_SERVER_IP needed - auto-discovery handles this!
```

#### Step 2: Install Arduino Libraries
In Arduino IDE:
1. Go to **Tools → Manage Libraries**
2. Search and install: **ArduinoJson** by Benoit Blanchon

#### Step 3: Flash WiFi Firmware with Auto-Discovery
1. Open `esp_code/esp32_wifi_vend/esp32_wifi_vend.ino` in Arduino IDE
2. Upload to ESP32
3. **The ESP32 automatically discovers the Flask server using UDP broadcast**
4. **No manual IP configuration required** - works on any network!

#### How Auto-Discovery Works
The WiFi ESP32 uses an intelligent UDP discovery system:

1. **ESP32 connects to WiFi** using your credentials
2. **ESP32 broadcasts UDP discovery request** on port 12346 to find Flask server
3. **Flask server responds** with its IP address automatically  
4. **ESP32 connects immediately** to discovered server via HTTP
5. **Normal operation begins** - no manual configuration needed!

**Benefits:**
- ✅ **Zero Configuration**: No need to find or configure server IP addresses
- ✅ **Dynamic Networks**: Works with DHCP and changing IP addresses  
- ✅ **Multi-Network**: Automatically adapts to different WiFi networks
- ✅ **Plug & Play**: Just power on ESP32 and it finds the server
- ✅ **Robust**: Handles network changes and reconnections automatically

#### Monitoring Auto-Discovery
You can monitor the discovery process:
1. **ESP32 Serial Monitor**: Shows discovery attempts and success messages
2. **Flask Server Console**: Shows incoming discovery requests and responses
3. **Web Interface**: Displays WiFi devices as they auto-connect
4. **Communication Monitor**: Real-time view of discovery and connection process

## 🌐 Web Interface

### Core Features
- **5 Slot Buttons**: Click to trigger vending
- **Real-time Status**: Success/error messages
- **Device Management**: Switch between Serial/WiFi ESP32 devices
- **Communication Monitor**: Real-time ESP32 communication log
- **Keyboard Support**: Press 1-5 keys to vend slots

### Device Switching
- **Auto-Select**: Automatically chooses best available device
- **Manual Selection**: Click on device in the device list
- **Priority**: Serial → WiFi → Simulation
- **Status Indicators**: Live connection status for each device

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/vend/<slot_id>` | POST | Trigger vending (slot 1-5) |
| `/status` | GET | System status and ESP32 info |
| `/esp32/devices/list` | GET | List all ESP32 devices |
| `/esp32/devices/select` | POST | Select active device |
| `/esp32/communication/mode` | GET | Current communication mode |

### Example API Usage:
```bash
# Vend slot 3
curl -X POST http://localhost:5000/vend/3

# Check system status
curl http://localhost:5000/status

# List ESP32 devices
curl http://localhost:5000/esp32/devices/list

# Select specific device
curl -X POST http://localhost:5000/esp32/devices/select \
  -H "Content-Type: application/json" \
  -d '{"device_id": "ESP32_6CC8404FE03C"}'
```

## 🚨 Troubleshooting

### 🔍 First Step: Run System Check
Before troubleshooting, always run the system check:

```bash
python check_system.py
```

The check will guide you to specific solutions based on what it finds.

### Common Issues

**❌ "Port not found" or "Access denied"**
- Close Arduino IDE Serial Monitor
- **Linux/Pi**: Add user to dialout group: `sudo usermod -a -G dialout $USER` (then logout/login)
- Try different USB port or cable

**❌ "No response from ESP32"**
- Verify baud rate is 115200
- Press ESP32 RESET button
- Check USB cable (some are power-only)
- Ensure correct firmware is uploaded

**❌ "WiFi connection failed"**
- Double-check SSID and password in ESP32 code
- Verify WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
- ~~Check Flask server IP address in ESP32 code~~ (Not needed with auto-discovery!)

**❌ "Auto-discovery not working"**
- **Verify network connectivity**: ESP32 and Flask server must be on same network subnet
- **Check firewall settings**: Ensure ports 5000 and 12346 are not blocked
- **Router configuration**: Some routers block UDP broadcast - check AP isolation settings
- **Network timing**: Allow 30-60 seconds for discovery on busy networks
- **Monitor discovery process**: Check ESP32 serial output for discovery attempts
- **Verify UDP service**: Flask console should show "UDP discovery service started"

**❌ "ESP32 connects but can't communicate"**
- **Check discovery success**: ESP32 serial monitor should show "Flask server discovered"
- **Verify HTTP connection**: After discovery, ESP32 should connect via HTTP to Flask
- **Network stability**: Ensure stable WiFi connection during operation
- **Server accessibility**: Test Flask server access from other devices on network

**❌ "Port 5000 already in use"**
```bash
# Linux/Pi
sudo netstat -tlnp | grep :5000
sudo kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**❌ Flask import errors**
```bash
pip install --upgrade flask pyserial requests
```

## 🔄 Communication Priority System

The system automatically uses the best available communication method:

1. **🔌 USB Serial** (highest priority) - Direct USB connection
2. **📡 WiFi ESP32** - Network-connected devices  
3. **🖥️ Simulation** - Console output for testing

Status messages show which method was used for each command.

## 📱 Mobile Access

The web interface is fully responsive and works on mobile devices:
- Access from same network: `http://[YOUR_IP]:5000`
- Touch-friendly buttons
- Real-time status updates
- Works on phones, tablets, any device with a browser

## 🔧 Technical Details: Auto-Discovery System

### UDP Discovery Protocol Implementation

#### Flask Server Side (`src/app.py`)
The Flask server runs a UDP discovery service in the background:

```python
# Automatic UDP discovery service on port 12346
def start_udp_discovery_service():
    def udp_discovery_handler():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 12346))  # Listen on port 12346
        while True:
            data, addr = sock.recvfrom(1024)
            if b"DISCOVER_FLASK_SERVER" in data:
                # Respond with server IP
                response = f"FLASK_SERVER_IP:{get_local_ip()}"
                sock.sendto(response.encode(), addr)
```

#### ESP32 Firmware Side (`esp32_wifi_vend.ino`)
The ESP32 implements intelligent discovery with retry logic:

```cpp
bool discoverFlaskServer() {
    WiFiUDP udp;
    udp.begin(12346);
    
    // Broadcast discovery request
    udp.beginPacket(WiFi.localIP() | ~WiFi.subnetMask(), 12346);
    udp.print("DISCOVER_FLASK_SERVER");
    udp.endPacket();
    
    // Wait for server response
    unsigned long timeout = millis() + 5000;
    while (millis() < timeout) {
        int packetSize = udp.parsePacket();
        if (packetSize) {
            String response = udp.readString();
            if (response.startsWith("FLASK_SERVER_IP:")) {
                // Extract and connect to discovered IP
                flaskServerIP = response.substring(16);
                return true;
            }
        }
        delay(100);
    }
    return false; // Discovery failed
}
```

### Discovery Process Flow
1. **Flask Server Startup**: UDP discovery service starts automatically on port 12346
2. **ESP32 WiFi Connection**: ESP32 connects to configured WiFi network
3. **Broadcast Discovery**: ESP32 sends UDP broadcast to find Flask server
4. **Server Response**: Flask server receives request and responds with its IP
5. **Connection Establishment**: ESP32 connects to discovered IP via HTTP
6. **Operation Begins**: Normal vending machine communication starts

### Network Requirements
- **Same Subnet**: ESP32 and Flask server must be on same network subnet
- **UDP Broadcast Support**: Network must allow UDP broadcast (most do by default)
- **Port Access**: Ports 5000 (Flask HTTP) and 12346 (UDP discovery) must be accessible
- **No Special Configuration**: Works with standard home/office network setups

## 🌟 Production Features

- **Multi-Device Support**: Handle multiple ESP32 devices simultaneously
- **Dynamic Device Detection**: Automatic ESP32 discovery and connection
- **Automatic Fallback**: Graceful degradation if hardware disconnects
- **Enhanced Monitoring**: Real-time communication logging and device status
- **Error Handling**: Comprehensive error reporting and recovery
- **Cross-Platform**: Runs on Windows, Linux, Raspberry Pi

## 📝 License

This project is open source and available under the MIT License.

---

**🎉 Your complete Flask vending machine system is ready!**

Choose USB serial for easy development and testing, or WiFi for production deployment with multiple devices. The system automatically handles communication and provides comprehensive debugging tools.