# 🥧 Raspberry Pi Vending Machine

Production-ready vending machine system optimized for **Raspberry Pi OS**. Features automatic ESP32 detection, enhanced debugging, and mobile-optimized interface.

## 🚀 Quick Setup

### **One-Command Setup:**
```bash
# One-time setup (creates virtual environment, installs dependencies)
chmod +x setup.sh && ./setup.sh

# Start server (run this each time you want to start the server)
chmod +x start.sh && ./start.sh
```

### **What the Setup Script Does:**
- ✅ **Checks Python 3**: Installs if missing
- ✅ **Creates Virtual Environment**: Isolated Python environment (only if needed)
- ✅ **Installs Dependencies**: Flask, PySerial, etc. (only if needed) 
- ✅ **Sets Up Permissions**: Adds user to dialout group for ESP32 access
- ✅ **Tests System**: Runs Pi-specific system test
- ✅ **Provides Next Steps**: Clear instructions for starting the server

The setup script is **smart** - it only installs what's missing, so it's fast on subsequent runs.

### **Manual Setup (Alternative):**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start server
python3 app.py
```

## 🧪 Testing the Pi System

### **Pi System Test**
Before starting the server, test your Raspberry Pi setup:

```bash
python3 test_system.py
```

### **Pi-Specific Test Features:**
- ✅ **ESP32 Detection**: Automatic port scanning on Pi
- ✅ **Serial Port Check**: Lists available `/dev/ttyUSB*` ports
- ✅ **Pi Flask App**: Tests Pi-optimized server
- ✅ **Network Access**: Shows Pi IP for remote access
- ✅ **Permissions**: Checks dialout group membership

### **Expected Pi Test Output:**
```
🥧 Raspberry Pi Vending Machine - Simple Test
=============================================
📦 Testing ESP32 Serial Module...
✅ ESP32 module imported successfully
✅ ESP32 connected on port: /dev/ttyUSB0

🔌 Checking Raspberry Pi Serial Ports...
✅ Found 1 serial port(s):
   📍 /dev/ttyUSB0: USB Serial

🌐 Testing Network Access...
✅ Pi IP Address: 192.168.1.150
🌐 Network access: http://192.168.1.150:5000
```

## 🔌 ESP32 Connection

### **🔥 Flashing ESP32 Firmware from Raspberry Pi**

You can flash ESP32 firmware directly from the Raspberry Pi using our automated script:

```bash
chmod +x flash_esp32.sh
./flash_esp32.sh
```

#### **🔧 Arduino CLI Installation**

If you prefer to install Arduino CLI separately or the automatic installation fails:

```bash
chmod +x install_arduino_cli.sh
./install_arduino_cli.sh
```

**What the installation script does:**
- ✅ **Detects system architecture** (ARM64, ARMv7, x86_64)
- ✅ **Downloads and installs Arduino CLI** (official installer + manual fallback)
- ✅ **Sets up ESP32 development environment**
- ✅ **Installs required libraries** (ArduinoJson)
- ✅ **Verifies installation** and shows connected boards
- ✅ **Provides usage examples** and next steps

#### **What the script does:**
1. **Installs Arduino CLI** (if not present)
2. **Detects ESP32 devices** automatically  
3. **Interactive firmware selection** (USB Serial or WiFi)
4. **Interactive port selection** from detected devices
5. **Compiles firmware** on the Pi
6. **Flashes ESP32** via USB
7. **Provides testing guidance**

#### **Interactive Workflow:**
```bash
🔥 ESP32 Firmware Flashing Tool
========================================================
✅ Arduino CLI found
🔍 Scanning for ESP32 devices...
📱 Found devices:
  1. /dev/ttyUSB0 - USB Serial Device
  2. /dev/ttyACM0 - Silicon Labs CP210x

🔥 Available firmware files:
1. ../esp32_mock_vend.ino (USB Serial Communication)
2. ../esp32_wifi_vend.ino (WiFi Communication)
3. Exit

Select firmware to flash (1/2/3): 1
📝 Selected: USB Serial Communication firmware

📱 Available ports:
1. /dev/ttyUSB0
2. /dev/ttyACM0

Select port (1-2): 1
📍 Selected port: /dev/ttyUSB0
🔨 Compiling firmware...
📤 Uploading firmware to ESP32...
✅ ESP32 flashed successfully!
```

#### **Firmware Options:**
- **Option 1**: `../esp32_mock_vend.ino` - USB Serial Communication
  - ✅ Direct USB connection to Pi
  - ✅ Simple setup, no WiFi needed
  - ✅ Best for development and testing
  
- **Option 2**: `../esp32_wifi_vend.ino` - WiFi Network Communication  
  - ✅ Wireless communication
  - ✅ Multiple ESP32 support
  - ⚠️ **Requires WiFi configuration before flashing**

#### **Port Selection:**
The script automatically detects and lists:
- **`/dev/ttyUSB0`, `/dev/ttyUSB1`** - USB-to-Serial adapters
- **`/dev/ttyACM0`, `/dev/ttyACM1`** - CDC/ACM devices
- **Device descriptions** when available

#### **Available firmware options:**
- **`../esp32_mock_vend.ino`**: USB Serial Communication
- **`../esp32_wifi_vend.ino`**: WiFi Network Communication

#### **WiFi Firmware Configuration:**
If selecting WiFi firmware, **you must edit the WiFi credentials first**:

```bash
# Edit the WiFi firmware file
nano ../esp32_wifi_vend.ino

# Update these lines:
const char* WIFI_SSID = "YOUR_WIFI_NETWORK";       // Your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // Your WiFi password  
const char* FLASK_SERVER_IP = "192.168.1.100";    // Your Pi's IP address
```

**Find your Pi's IP address:**
```bash
hostname -I
# Example output: 192.168.1.150
```

The script will prompt you to confirm WiFi credentials are updated before flashing.

#### **Manual Arduino CLI Setup** (if needed):

**Option 1: Use our installation script (recommended)**
```bash
chmod +x install_arduino_cli.sh
./install_arduino_cli.sh
```

**Option 2: Manual installation**
```bash
# Install Arduino CLI
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo mv bin/arduino-cli /usr/local/bin/

# Setup ESP32 support
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli lib install "ArduinoJson"

# Flash firmware manually
arduino-cli compile --fqbn esp32:esp32:esp32 ../esp32_mock_vend.ino
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 ../esp32_mock_vend.ino
```

#### **🚨 Flashing Troubleshooting:**

**❌ "No serial devices found"**
```bash
# Check USB connection
lsusb | grep -i "cp210\|ch340\|esp32"

# Check if devices appear
ls /dev/ttyUSB* /dev/ttyACM*

# Add user to dialout group  
sudo usermod -a -G dialout $USER
# Then logout and login again
```

**❌ "Failed to upload firmware"**
```bash
# Try holding BOOT button during upload
# Or press BOOT + RESET, release RESET, then release BOOT

# Check if port is correct
arduino-cli board list

# Manual upload with different baud rate
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 --upload-field baud=460800 firmware.ino
```

**❌ "Compilation failed"** 
```bash
# Update Arduino CLI and cores
arduino-cli core update-index
arduino-cli core upgrade

# Reinstall ESP32 core
arduino-cli core uninstall esp32:esp32
arduino-cli core install esp32:esp32
```

**❌ "ArduinoJson library not found"**
```bash
# Reinstall library
arduino-cli lib install "ArduinoJson"

# Or install specific version
arduino-cli lib install "ArduinoJson@6.21.3"
```

### **USB Serial (Recommended)**

1. **Connect ESP32** via USB cable to Raspberry Pi
2. **Check permissions:**
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```
3. **Flash firmware:** Use `./flash_esp32.sh` or upload `../esp32_mock_vend.ino` manually
4. **Auto-detection:** System automatically finds ESP32 port

### **Common Ports:**
- `/dev/ttyUSB0` - Most USB-to-Serial adapters
- `/dev/ttyACM0` - Some ESP32 boards  
- `/dev/serial0` - GPIO serial pins

### **WiFi Network**
1. **Flash WiFi firmware:** Use `./flash_esp32.sh` and select WiFi option
2. **Configure WiFi credentials** in ESP32 code before flashing
3. **ESP32 auto-registers** with Raspberry Pi server

## 🌐 Access Interface

### **Local Access:**
```
http://localhost:5000
```

### **Network Access:**
```bash
# Find Pi IP address
hostname -I
# Then access from any device: http://[PI_IP]:5000
```

### **Mobile Optimized:**
- Touch-friendly interface
- Responsive design
- Real-time status updates
- Debug console

## 🔧 Pi-Specific Features

### **Auto-Detection**
- Automatic ESP32 port scanning
- Smart device recognition
- Fallback to simulation mode

### **Enhanced Debugging**
- Web-based debug console
- Real-time ESP32 communication log
- System status monitoring
- Connection diagnostics

### **Production Ready**
- Systemd service configuration
- Startup scripts included
- Error handling and recovery
- Performance optimized for Pi hardware

## 🚨 Troubleshooting

### **🔍 First Step: Run Pi System Test**
Always start troubleshooting by running the Pi-specific test:

```bash
python3 test_system.py
```

This will check:
- ESP32 connection and port detection
- Serial port permissions (dialout group)
- Pi Flask app functionality
- Network configuration
- System-specific issues

### **ESP32 Not Detected:**
```bash
# Check USB devices
lsusb
# Should show: "Silicon Labs CP210x" or "QinHeng Electronics"

# Check serial ports
ls /dev/ttyUSB* /dev/ttyACM*

# Check permissions
groups
# Should include 'dialout'
```

### **Permission Denied:**
```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

### **Flask Server Issues:**
```bash
# Check if port in use
sudo netstat -tlnp | grep :5000

# Kill conflicting process
sudo kill -9 <PID>

# Check system logs
journalctl -f
```

## 🎯 Production Deployment

### **System Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/vending-machine.service

# Add content:
[Unit]
Description=Raspberry Pi Vending Machine
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rasp_pi
Environment=PATH=/home/pi/rasp_pi/venv/bin
ExecStart=/home/pi/rasp_pi/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable service
sudo systemctl enable vending-machine.service
sudo systemctl start vending-machine.service
```

### **Auto-Start on Boot:**
```bash
# Add to /etc/rc.local (before 'exit 0'):
cd /home/pi/rasp_pi
sudo -u pi /home/pi/rasp_pi/venv/bin/python app.py &
```

## 📊 Monitoring

### **System Status:**
```bash
# View service status
sudo systemctl status vending-machine.service

# View logs
sudo journalctl -u vending-machine.service -f

# Monitor resources
htop
```

### **ESP32 Monitoring:**
```bash
# Watch USB devices
watch -n 1 lsusb

# Monitor serial ports
watch -n 1 "ls -la /dev/ttyUSB* /dev/ttyACM*"
```

## 🔄 Communication Flow

```
Mobile Browser → Raspberry Pi → ESP32 → Vending Hardware
      ↑              ↑          ↓            ↓
  Touch Interface  Flask Server  USB/WiFi   Motor Control
  Web UI          HTTP API      Commands    Physical Action
```

## 🎮 Remote Access

### **SSH Access:**
```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Connect from another device
ssh pi@[PI_IP_ADDRESS]
```

### **Web Interface from Anywhere:**
Set up port forwarding on your router:
- External Port: 8080
- Internal Port: 5000  
- Device: Raspberry Pi IP

Access via: `http://[YOUR_PUBLIC_IP]:8080`

## 💡 Optimization Tips

### **Performance:**
- Use Class 10 MicroSD card
- Enable GPU memory split: `sudo raspi-config`
- Disable unused services
- Use lightweight desktop environment

### **Reliability:**
- Use quality USB cables
- Ensure stable power supply
- Enable hardware watchdog
- Implement log rotation

---

**🎉 Your Raspberry Pi vending machine is production-ready!**

The system provides automatic ESP32 detection, comprehensive debugging tools, and mobile-optimized interface for reliable operation.