# 🏪 Flask Vending Machine

A complete vending machine control system with Flask backend and ESP32 hardware interface. Supports both USB serial and WiFi communication with automatic fallback and cross-platform compatibility.

## ✨ Features

- **Web-based Interface**: Professional 5-slot vending machine UI
- **Dual Communication**: USB serial + WiFi ESP32 support with auto-fallback
- **Cross-Platform**: Windows development + Raspberry Pi production ready
- **Smart Detection**: Automatic ESP32 port/device detection
- **Complete Setup**: One-command installation and startup
- **Hardware Ready**: Real ESP32 firmware included

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

### 📡 Method 2: WiFi Network (Production)

#### Step 1: Configure WiFi Credentials
Edit `esp_code/esp32_wifi_vend/esp32_wifi_vend.ino`:
```cpp
const char* WIFI_SSID = "YOUR_WIFI_NETWORK";      // Your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Your WiFi password
const char* FLASK_SERVER_IP = "192.168.1.100";   // Your computer's IP
```

#### Step 2: Install Arduino Libraries
In Arduino IDE:
1. Go to **Tools → Manage Libraries**
2. Search and install: **ArduinoJson** by Benoit Blanchon

#### Step 3: Flash WiFi Firmware
1. Open `esp_code/esp32_wifi_vend/esp32_wifi_vend.ino` in Arduino IDE
2. Upload to ESP32

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
- Check Flask server IP address in ESP32 code

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