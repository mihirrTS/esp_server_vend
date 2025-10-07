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
├── rasp_pi/                       # 🥧 Raspberry Pi optimized version
│   ├── app.py                     # Enhanced Pi server
│   ├── setup_and_run.sh           # Complete Pi setup script
│   ├── flash_esp32.sh             # ESP32 flashing tool (Arduino CLI)
│   ├── install_arduino_cli.sh     # Arduino CLI installation script
│   ├── test_system.py             # Pi system test script
│   └── templates/, static/        # Pi web interface
├── esp32_mock_vend.ino           # 🔌 ESP32 USB serial firmware
├── esp32_wifi_vend.ino           # 📡 ESP32 WiFi firmware
├── esp32_serial.py               # Python serial communication module
├── setup_and_run.bat             # 🚀 Windows setup script
├── test_system.py                # 🧪 System test script
└── requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### **Automated Setup (Recommended)**

**Windows:**
```powershell
.\setup_and_run.bat
```

**Linux/Raspberry Pi:**
```bash
cd rasp_pi
chmod +x setup_and_run.sh && ./setup_and_run.sh
```

### **Manual Setup**

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Server:**
   ```bash
   python src/app.py
   ```

3. **Open Interface:**
   Navigate to `http://localhost:5000`

## � Testing the System

### **Quick System Test**
Before starting the server, test your setup:

**Windows:**
```powershell
python test_system.py
```

**Raspberry Pi:**
```bash
cd rasp_pi
python3 test_system.py
```

### **What the Test Checks:**
- ✅ **ESP32 Serial Module**: Import and connection test
- ✅ **Flask Application**: Server functionality
- ✅ **System Status**: Overall health check
- ✅ **Setup Guidance**: Next steps if issues found

### **Expected Output:**
```
🧪 Flask Vending Machine - Simple Test
========================================
📦 Testing ESP32 Serial Module...
✅ ESP32 module imported successfully
⚠️ ESP32 not connected (will use simulation)

🌐 Testing Flask Server...
✅ Flask app imported successfully
✅ Flask app context created

📡 Testing Server Connection...
⚠️ Server not running - start with: python src/app.py
```

## �🤖 ESP32 Communication Setup

### **📋 Choose Your Method:**

| Method | Best For | Firmware | Range | Setup |
|--------|----------|----------|--------|--------|
| **🔌 USB Serial** | Development, Testing | `esp32_mock_vend.ino` | Cable length | Plug & play |
| **📡 WiFi Network** | Production, Multiple devices | `esp32_wifi_vend.ino` | WiFi range | Network config |
| **🖥️ Simulation** | Testing without hardware | None needed | N/A | Just run Flask |

### **🔌 Method 1: USB Serial (Recommended for Testing)**

#### **Step 1: Connect Hardware**
1. Connect ESP32 to computer via USB cable
2. Install ESP32 drivers if needed (CP210x or CH340)

#### **Step 2: Find Serial Port**

**Windows:**
```powershell
# Check Device Manager → Ports (COM & LPT)
# Look for "Silicon Labs CP210x" - note the COM port (e.g., COM3)
```

**Linux/Raspberry Pi:**
```bash
# List available ports
ls /dev/ttyUSB* /dev/ttyACM*
# Usually: /dev/ttyUSB0

# Check permissions (add user to dialout group)
sudo usermod -a -G dialout $USER
# Then logout and login again
```

#### **Step 3: Flash ESP32 Firmware**
1. Open `esp32_mock_vend.ino` in Arduino IDE
2. Select board: **ESP32 Dev Module**
3. Select correct port
4. Upload code

#### **Step 4: Verify Connection**
1. Open Serial Monitor (115200 baud)
2. Press ESP32 RESET button
3. Should see:
   ```
   ESP32 Mock Vending Machine v1.0
   System ready!
   Waiting for commands from Flask server...
   ```

#### **Step 5: Test with Flask**
1. Start Flask server: `python src/app.py`
2. Should see: "✅ ESP32 connected via serial"
3. Click slot buttons - commands go via USB

### **📡 Method 2: WiFi Network (Production)**

#### **Step 1: Configure WiFi Credentials**
Edit `esp32_wifi_vend.ino`:
```cpp
const char* WIFI_SSID = "YOUR_WIFI_NETWORK";      // Your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Your WiFi password
const char* FLASK_SERVER_IP = "192.168.1.100";   // Your computer's IP
```

#### **Step 2: Find Your Computer's IP**
**Windows:**
```powershell
ipconfig
# Look for "IPv4 Address" under active network
```

**Linux:**
```bash
ip addr show
# Or: hostname -I
```

#### **Step 3: Install Arduino Libraries**
In Arduino IDE:
1. Go to **Tools → Manage Libraries**
2. Search and install: **ArduinoJson** by Benoit Blanchon

#### **Step 4: Flash WiFi Firmware**
1. Open `esp32_wifi_vend.ino` in Arduino IDE
2. Upload to ESP32

#### **Step 5: Test WiFi Connection**
1. Start Flask server: `python src/app.py`
2. ESP32 Serial Monitor should show:
   ```
   WiFi connected!
   IP address: 192.168.1.101
   Registration successful!
   System ready for network commands!
   ```
3. Web interface shows: "ESP32: 1 device(s) connected"

### **🔥 Raspberry Pi: Direct ESP32 Flashing**

If using Raspberry Pi, you can flash ESP32 firmware directly without Arduino IDE:

```bash
cd rasp_pi
chmod +x flash_esp32.sh
./flash_esp32.sh
```

**Features:**
- ✅ **Interactive firmware selection** (USB Serial or WiFi)
- ✅ **Automatic port detection** and selection
- ✅ **Arduino CLI auto-installation**
- ✅ **WiFi credential verification** for WiFi firmware

See [rasp_pi/README.md](rasp_pi/README.md) for complete Raspberry Pi flashing guide.

## 🌐 Web Interface

### **Core Features**
- **5 Slot Buttons**: Click to trigger vending
- **Real-time Status**: Success/error messages
- **Action Log**: Last vending action with timestamp
- **Keyboard Support**: Press 1-5 keys to vend slots
- **Communication Status**: Shows serial/WiFi/simulation mode

### **Advanced Features**
- **Custom Slot Names**: Assign names like "Coke", "Chips"
- **Debug Console**: Real-time ESP32 communication log
- **Device Management**: View connected ESP32 devices
- **Command History**: Track all vending operations

## 🥧 Raspberry Pi Setup

For production deployment on Raspberry Pi, use the optimized version in the `rasp_pi/` folder:

### **Quick Pi Setup:**
```bash
cd rasp_pi
chmod +x install.sh start.sh
./install.sh    # Complete setup (run once)
./start.sh      # Start server
```

### **Pi Features:**
- **Auto-Detection**: Automatic ESP32 port detection
- **Enhanced Debugging**: Web-based debug console
- **Production Ready**: Systemd service configuration
- **Mobile Optimized**: Touch-friendly interface

See **[rasp_pi/README.md](rasp_pi/README.md)** for complete Raspberry Pi setup guide.

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/vend/<slot_id>` | POST | Trigger vending (slot 1-5) |
| `/status` | GET | System status and ESP32 info |
| `/esp32/devices` | GET | List connected ESP32 devices |
| `/esp32/register` | POST | ESP32 WiFi registration |
| `/esp32/commands/<device_id>` | GET | Polling endpoint for ESP32 |

### **Example API Usage:**
```bash
# Vend slot 3
curl -X POST http://localhost:5000/vend/3

# Check system status
curl http://localhost:5000/status

# List ESP32 devices
curl http://localhost:5000/esp32/devices
```

## 🔧 Communication Priority System

The system automatically uses the best available communication method:

1. **🔌 USB Serial** (highest priority) - Direct USB connection
2. **📡 WiFi ESP32** - Network-connected devices
3. **🖥️ Simulation** - Console output for testing

Status messages show which method was used for each command.

## 🚨 Troubleshooting

### **🔍 First Step: Run System Test**
Before troubleshooting, always run the system test to identify issues:

**Windows:**
```powershell
python test_system.py
```

**Raspberry Pi:**
```bash
cd rasp_pi && python3 test_system.py
```

The test will guide you to specific solutions based on what it finds.

### **Serial Communication Issues**

**❌ "Port not found" or "Access denied"**
- Close Arduino IDE Serial Monitor
- Check correct COM port in Device Manager (Windows)
- Add user to dialout group (Linux): `sudo usermod -a -G dialout $USER`
- Try different USB port or cable

**❌ "No response from ESP32"**
- Verify baud rate is 115200
- Press ESP32 RESET button
- Check USB cable (some are power-only)
- Ensure correct firmware is uploaded

### **WiFi Communication Issues**

**❌ "WiFi connection failed"**
- Double-check SSID and password in ESP32 code
- Verify WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
- Check ESP32 is within WiFi range

**❌ "Registration failed"**
- Verify Flask server IP address in ESP32 code
- Check Flask server is running and accessible
- Allow Python through Windows Firewall

### **General Issues**

**❌ "Port 5000 already in use"**
```powershell
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux
sudo netstat -tlnp | grep :5000
sudo kill -9 <PID>
```

**❌ Flask import errors**
```bash
pip install --upgrade flask pyserial
```

## 🔄 Development

### **Project Dependencies**
- **Flask 2.3+**: Web framework
- **PySerial 3.5**: ESP32 communication
- **Python 3.7+**: Required runtime

### **File Structure**
- **Backend Logic**: `src/app.py`
- **Frontend UI**: `src/templates/index.html`
- **Styling**: `src/static/css/styles.css`
- **JavaScript**: `src/static/js/app.js`
- **ESP32 Firmware**: `esp32_mock_vend.ino` / `esp32_wifi_vend.ino`

### **Hardware Integration**
Replace simulation code with actual hardware control:

**Motor Control Example:**
```cpp
// In ESP32 firmware
#include <Stepper.h>
Stepper motor1(200, SLOT_1_PIN, SLOT_1_PIN+1);

void vendSlot(int slot) {
    motor1.step(200);  // Rotate motor
    // Add sensor checking, error handling
}
```

## 📱 Mobile Access

The web interface is fully responsive and works great on mobile:
- Access from same network: `http://[YOUR_IP]:5000`
- Touch-friendly slot buttons
- Real-time status updates
- Works on phones, tablets, any device with a browser

## 🌟 Production Features

- **Hybrid Communication**: Multiple ESP32 devices via WiFi + USB
- **Automatic Fallback**: Graceful degradation if hardware disconnects
- **Error Handling**: Comprehensive error reporting and recovery
- **Logging**: Detailed operation logs for troubleshooting
- **Status Monitoring**: Real-time system health information
- **Cross-Platform**: Runs on Windows, Linux, Raspberry Pi

## 📝 License

This project is open source and available under the MIT License.

---

**🎉 Your complete Flask vending machine system is ready!**

Choose USB serial for easy development and testing, or WiFi for production deployment with multiple devices. The system automatically handles communication and provides comprehensive debugging tools.