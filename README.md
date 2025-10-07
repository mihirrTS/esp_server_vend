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
| **� WiFi Network** | Production, Multiple devices | `esp32_wifi_vend.ino` | WiFi range | Network config |
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

├── setup.bat                      # 🚀 Windows setup script│   ├── test_system.py             # Pi system test script

├── start.bat                      # ▶️ Windows start server script│   └── templates/, static/        # Pi web interface

└── requirements.txt              # Python dependencies├── esp32_mock_vend/               # 🔌 ESP32 USB serial firmware folder

```│   └── esp32_mock_vend.ino        # ESP32 USB serial firmware

├── esp32_wifi_vend/               # 📡 ESP32 WiFi firmware folder  

## 🚀 Quick Start│   └── esp32_wifi_vend.ino        # ESP32 WiFi firmware

├── esp32_serial.py               # Python serial communication module

### **Windows Setup:**├── setup.bat                      # 🚀 Windows setup script

```powershell├── start.bat                      # ▶️ Windows start server script

# Step 1: One-time setup (only run this once)├── test_system.py                # 🧪 System test script

.\setup.bat└── requirements.txt              # Python dependencies

```

# Step 2: Start server (run this each time)

.\start.bat## 🚀 Quick Start



# Step 3: Open web interface### **New User? Start Here:**

# Browser will open automatically or go to: http://localhost:5000

```**Windows:**

```powershell

### **Linux/Raspberry Pi Setup:**# Step 1: One-time setup (only run this once)

```bash.\setup.bat

# Step 1: Install Python and pip (if not already installed)

sudo apt update# Step 2: Start server (run this each time)

sudo apt install python3 python3-pip python3-venv -y.\start.bat

```

# Step 2: Create virtual environment and install dependencies

python3 -m venv venv**Linux/Raspberry Pi:**

source venv/bin/activate```bash

pip install -r requirements.txtcd rasp_pi



# Step 3: Start server# Step 1: One-time setup (only run this once)

python src/app.pychmod +x setup.sh && ./setup.sh



# Step 4: Open web interface# Step 2: Start server (run this each time)  

# Go to: http://localhost:5000 or http://[YOUR_PI_IP]:5000chmod +x start.sh && ./start.sh

``````



## 🥧 Raspberry Pi Production Setup### ### **📋 Simple Workflow:**



For production deployment on Raspberry Pi OS:```

First Time:     .\setup.bat  →  .\start.bat  →  http://localhost:5000

### **Quick Pi Setup:**Every Time:     .\start.bat  →  http://localhost:5000

```bash```

# 1. Update system

sudo apt update && sudo apt upgrade -y**What each script does:**

- **`setup.bat/setup.sh`**: Prepares your computer (virtual environment, dependencies)

# 2. Install required packages- **`start.bat/start.sh`**: Starts the web server 

sudo apt install python3 python3-pip python3-venv git -y- **Web interface**: `http://localhost:5000` - click buttons to vend!



# 3. Clone and setup project### **What the Setup Script Does:**

git clone <your-repo-url> flask-vending-machine- ✅ **Checks Python Installation**: Verifies Python is available

cd flask-vending-machine- ✅ **Creates Virtual Environment**: Isolated Python environment (only if needed)

- ✅ **Installs Dependencies**: Flask, PySerial, etc. (only if needed)

# 4. Create Python virtual environment- ✅ **Tests System**: Runs system test to verify everything works

python3 -m venv venv- ✅ **Provides Next Steps**: Clear instructions for starting the server

source venv/bin/activate

### **Manual Setup (Alternative)**

# 5. Install Python dependencies

pip install -r requirements.txt1. **Install Dependencies:**

   ```bash

# 6. Add user to dialout group for serial access   pip install -r requirements.txt

sudo usermod -a -G dialout $USER   ```



# 7. Test system2. **Start Server:**

python check_system.py   ```bash

   python src/app.py

# 8. Start server   ```

python src/app.py

```3. **Open Interface:**

   Navigate to `http://localhost:5000`

### **Pi Auto-Start Service (Optional):**

Create a systemd service to auto-start the vending machine:## � Testing the System



```bash### **Quick System Test**

# Create service fileBefore starting the server, test your setup:

sudo nano /etc/systemd/system/vending-machine.service

```**Windows:**

```powershell

Add this content:python test_system.py

```ini```

[Unit]

Description=Flask Vending Machine**Raspberry Pi:**

After=network.target```bash

cd rasp_pi

[Service]python3 test_system.py

Type=simple```

User=pi

WorkingDirectory=/home/pi/flask-vending-machine### **What the Test Checks:**

Environment=PATH=/home/pi/flask-vending-machine/venv/bin- ✅ **ESP32 Serial Module**: Import and connection test

ExecStart=/home/pi/flask-vending-machine/venv/bin/python src/app.py- ✅ **Flask Application**: Server functionality

Restart=always- ✅ **System Status**: Overall health check

- ✅ **Setup Guidance**: Next steps if issues found

[Install]

WantedBy=multi-user.target### **Expected Output:**

``````

🧪 Flask Vending Machine - Simple Test

Enable and start the service:========================================

```bash📦 Testing ESP32 Serial Module...

sudo systemctl enable vending-machine.service✅ ESP32 module imported successfully

sudo systemctl start vending-machine.service⚠️ ESP32 not connected (will use simulation)

sudo systemctl status vending-machine.service

```🌐 Testing Flask Server...

✅ Flask app imported successfully

### **Pi Network Access:**✅ Flask app context created

```bash

# Find your Pi's IP address📡 Testing Server Connection...

hostname -I⚠️ Server not running - start with: python src/app.py

```

# Access from other devices on the network:

# http://[PI_IP_ADDRESS]:5000## �🤖 ESP32 Communication Setup

# Example: http://192.168.1.100:5000

```### **📋 Choose Your Method:**



## 🧪 Testing the System| Method | Best For | Firmware | Range | Setup |

|--------|----------|----------|--------|--------|

Before starting the server, test your setup:| **🔌 USB Serial** | Development, Testing | `esp32_mock_vend/esp32_mock_vend.ino` | Cable length | Plug & play |

| **📡 WiFi Network** | Production, Multiple devices | `esp32_wifi_vend/esp32_wifi_vend.ino` | WiFi range | Network config |

```bash| **🖥️ Simulation** | Testing without hardware | None needed | N/A | Just run Flask |

python check_system.py

```### **🔌 Method 1: USB Serial (Recommended for Testing)**



### **What the Test Checks:**#### **Step 1: Connect Hardware**

- ✅ **System Requirements**: OS, Python version, required files1. Connect ESP32 to computer via USB cable

- ✅ **Python Environment**: Dependencies installation 2. Install ESP32 drivers if needed (CP210x or CH340)

- ✅ **ESP32 Module**: Import and connection test

- ✅ **Flask Application**: Server functionality#### **Step 2: Find Serial Port**

- ✅ **Server Connection**: Live server status (if running)

**Windows:**

### **Expected Output:**```powershell

```# Check Device Manager → Ports (COM & LPT)

============================================================# Look for "Silicon Labs CP210x" - note the COM port (e.g., COM3)

 Flask Vending Machine - System Check```

============================================================

🧪 Running System Requirements test...**Linux/Raspberry Pi:**

✅ Operating System: Linux```bash

✅ Found: src/app.py# List available ports

✅ Found: esp32_serial.pyls /dev/ttyUSB* /dev/ttyACM*

✅ Found: requirements.txt# Usually: /dev/ttyUSB0

✅ All required files present

# Check permissions (add user to dialout group)

🧪 Running Python Environment test...sudo usermod -a -G dialout $USER

✅ Python version compatible# Then logout and login again

✅ flask: Flask web framework - Available```

✅ serial: PySerial for ESP32 communication - Available

✅ requests: HTTP requests library - Available#### **Step 3: Flash ESP32 Firmware**

```1. Open `esp32_mock_vend/esp32_mock_vend.ino` in Arduino IDE

2. Select board: **ESP32 Dev Module**

## 🤖 ESP32 Communication Setup3. Select correct port

4. Upload code

### **📋 Choose Your Method:**

#### **Step 4: Verify Connection**

| Method | Best For | Firmware | Range | Setup |1. Open Serial Monitor (115200 baud)

|--------|----------|----------|--------|--------|2. Press ESP32 RESET button

| **🔌 USB Serial** | Development, Testing | `esp32_mock_vend.ino` | Cable length | Plug & play |3. Should see:

| **📡 WiFi Network** | Production, Multiple devices | `esp32_wifi_vend.ino` | WiFi range | Network config |   ```

| **🖥️ Simulation** | Testing without hardware | None needed | N/A | Just run Flask |   ESP32 Mock Vending Machine v1.0

   System ready!

### **🔌 Method 1: USB Serial (Recommended for Testing)**   Waiting for commands from Flask server...

   ```

#### **Step 1: Connect Hardware**

1. Connect ESP32 to computer via USB cable#### **Step 5: Test with Flask**

2. Install ESP32 drivers if needed (CP210x or CH340)1. Start Flask server: `python src/app.py`

2. Should see: "✅ ESP32 connected via serial"

#### **Step 2: Flash ESP32 Firmware**3. Click slot buttons - commands go via USB

1. Open `esp_code/esp32_mock_vend/esp32_mock_vend.ino` in Arduino IDE

2. Select board: **ESP32 Dev Module**### **📡 Method 2: WiFi Network (Production)**

3. Select correct port

4. Upload code#### **Step 1: Configure WiFi Credentials**

Edit `esp32_wifi_vend/esp32_wifi_vend.ino`:

#### **Step 3: Verify Connection**```cpp

1. Open Serial Monitor (115200 baud)const char* WIFI_SSID = "YOUR_WIFI_NETWORK";      // Your WiFi name

2. Press ESP32 RESET buttonconst char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Your WiFi password

3. Should see:const char* FLASK_SERVER_IP = "192.168.1.100";   // Your computer's IP

   ``````

   ESP32 Mock Vending Machine v1.0

   System ready!#### **Step 2: Find Your Computer's IP**

   Waiting for commands from Flask server...**Windows:**

   ``````powershell

ipconfig

### **📡 Method 2: WiFi Network (Production)**# Look for "IPv4 Address" under active network

```

#### **Step 1: Configure WiFi Credentials**

Edit `esp_code/esp32_wifi_vend/esp32_wifi_vend.ino`:**Linux:**

```cpp```bash

const char* WIFI_SSID = "YOUR_WIFI_NETWORK";      // Your WiFi nameip addr show

const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // Your WiFi password# Or: hostname -I

const char* FLASK_SERVER_IP = "192.168.1.100";   // Your computer's IP```

```

#### **Step 3: Install Arduino Libraries**

#### **Step 2: Install Arduino Libraries**In Arduino IDE:

In Arduino IDE:1. Go to **Tools → Manage Libraries**

1. Go to **Tools → Manage Libraries**2. Search and install: **ArduinoJson** by Benoit Blanchon

2. Search and install: **ArduinoJson** by Benoit Blanchon

#### **Step 4: Flash WiFi Firmware**

#### **Step 3: Flash WiFi Firmware**1. Open `esp32_wifi_vend/esp32_wifi_vend.ino` in Arduino IDE

1. Open `esp_code/esp32_wifi_vend/esp32_wifi_vend.ino` in Arduino IDE2. Upload to ESP32

2. Upload to ESP32

#### **Step 5: Test WiFi Connection**

## 🌐 Web Interface1. Start Flask server: `python src/app.py`

2. ESP32 Serial Monitor should show:

### **Core Features**   ```

- **5 Slot Buttons**: Click to trigger vending   WiFi connected!

- **Real-time Status**: Success/error messages   IP address: 192.168.1.101

- **Device Management**: Switch between Serial/WiFi ESP32 devices   Registration successful!

- **Communication Monitor**: Real-time ESP32 communication log   System ready for network commands!

- **Keyboard Support**: Press 1-5 keys to vend slots   ```

3. Web interface shows: "ESP32: 1 device(s) connected"

### **Device Switching**

- **Auto-Select**: Automatically chooses best available device### **🔥 Raspberry Pi: Direct ESP32 Flashing**

- **Manual Selection**: Click on device in the device list

- **Priority**: Serial → WiFi → SimulationIf using Raspberry Pi, you can flash ESP32 firmware directly without Arduino IDE:

- **Status Indicators**: Live connection status for each device

```bash

## 🔧 API Endpointscd rasp_pi

chmod +x flash_esp32.sh

| Endpoint | Method | Description |./flash_esp32.sh

|----------|--------|-------------|```

| `/` | GET | Web interface |

| `/vend/<slot_id>` | POST | Trigger vending (slot 1-5) |**Features:**

| `/status` | GET | System status and ESP32 info |- ✅ **Interactive firmware selection** (USB Serial or WiFi)

| `/esp32/devices/list` | GET | List all ESP32 devices |- ✅ **Automatic port detection** and selection

| `/esp32/devices/select` | POST | Select active device |- ✅ **Arduino CLI auto-installation**

| `/esp32/communication/mode` | GET | Current communication mode |- ✅ **WiFi credential verification** for WiFi firmware



### **Example API Usage:**See [rasp_pi/README.md](rasp_pi/README.md) for complete Raspberry Pi flashing guide.

```bash

# Vend slot 3## 🌐 Web Interface

curl -X POST http://localhost:5000/vend/3

### **Core Features**

# Check system status- **5 Slot Buttons**: Click to trigger vending

curl http://localhost:5000/status- **Real-time Status**: Success/error messages

- **Action Log**: Last vending action with timestamp

# List ESP32 devices- **Keyboard Support**: Press 1-5 keys to vend slots

curl http://localhost:5000/esp32/devices/list- **Communication Status**: Shows serial/WiFi/simulation mode



# Select specific device### **Advanced Features**

curl -X POST http://localhost:5000/esp32/devices/select \- **Custom Slot Names**: Assign names like "Coke", "Chips"

  -H "Content-Type: application/json" \- **Debug Console**: Real-time ESP32 communication log

  -d '{"device_id": "ESP32_6CC8404FE03C"}'- **Device Management**: View connected ESP32 devices

```- **Command History**: Track all vending operations



## 🚨 Troubleshooting## 🥧 Raspberry Pi Setup



### **🔍 First Step: Run System Check**For production deployment on Raspberry Pi, use the optimized version in the `rasp_pi/` folder:

Before troubleshooting, always run the system check:

### **Quick Pi Setup:**

```bash```bash

python check_system.pycd rasp_pi

```chmod +x install.sh start.sh

./install.sh    # Complete setup (run once)

The check will guide you to specific solutions based on what it finds../start.sh      # Start server

```

### **Common Issues**

### **Pi Features:**

**❌ "Port not found" or "Access denied"**- **Auto-Detection**: Automatic ESP32 port detection

- Close Arduino IDE Serial Monitor- **Enhanced Debugging**: Web-based debug console

- **Linux/Pi**: Add user to dialout group: `sudo usermod -a -G dialout $USER` (then logout/login)- **Production Ready**: Systemd service configuration

- Try different USB port or cable- **Mobile Optimized**: Touch-friendly interface



**❌ "No response from ESP32"**See **[rasp_pi/README.md](rasp_pi/README.md)** for complete Raspberry Pi setup guide.

- Verify baud rate is 115200

- Press ESP32 RESET button## 🔧 API Endpoints

- Check USB cable (some are power-only)

- Ensure correct firmware is uploaded| Endpoint | Method | Description |

|----------|--------|-------------|

**❌ "WiFi connection failed"**| `/` | GET | Web interface |

- Double-check SSID and password in ESP32 code| `/vend/<slot_id>` | POST | Trigger vending (slot 1-5) |

- Verify WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)| `/status` | GET | System status and ESP32 info |

- Check Flask server IP address in ESP32 code| `/esp32/devices` | GET | List connected ESP32 devices |

| `/esp32/register` | POST | ESP32 WiFi registration |

**❌ "Port 5000 already in use"**| `/esp32/commands/<device_id>` | GET | Polling endpoint for ESP32 |

```bash

# Linux/Pi### **Example API Usage:**

sudo netstat -tlnp | grep :5000```bash

sudo kill -9 <PID># Vend slot 3

curl -X POST http://localhost:5000/vend/3

# Windows

netstat -ano | findstr :5000# Check system status

taskkill /PID <PID> /Fcurl http://localhost:5000/status

```

# List ESP32 devices

**❌ Flask import errors**curl http://localhost:5000/esp32/devices

```bash```

pip install --upgrade flask pyserial requests

```## 🔧 Communication Priority System



## 🔄 Communication Priority SystemThe system automatically uses the best available communication method:



The system automatically uses the best available communication method:1. **🔌 USB Serial** (highest priority) - Direct USB connection

2. **📡 WiFi ESP32** - Network-connected devices

1. **🔌 USB Serial** (highest priority) - Direct USB connection3. **🖥️ Simulation** - Console output for testing

2. **📡 WiFi ESP32** - Network-connected devices  

3. **🖥️ Simulation** - Console output for testingStatus messages show which method was used for each command.



Status messages show which method was used for each command.## 🚨 Troubleshooting



## 📱 Mobile Access### **🔍 First Step: Run System Test**

Before troubleshooting, always run the system test to identify issues:

The web interface is fully responsive and works on mobile devices:

- Access from same network: `http://[YOUR_IP]:5000`**Windows:**

- Touch-friendly buttons```powershell

- Real-time status updatespython test_system.py

- Works on phones, tablets, any device with a browser```



## 🌟 Production Features**Raspberry Pi:**

```bash

- **Multi-Device Support**: Handle multiple ESP32 devices simultaneouslycd rasp_pi && python3 test_system.py

- **Dynamic Device Detection**: Automatic ESP32 discovery and connection```

- **Automatic Fallback**: Graceful degradation if hardware disconnects

- **Enhanced Monitoring**: Real-time communication logging and device statusThe test will guide you to specific solutions based on what it finds.

- **Error Handling**: Comprehensive error reporting and recovery

- **Cross-Platform**: Runs on Windows, Linux, Raspberry Pi### **Serial Communication Issues**



## 📝 License**❌ "Port not found" or "Access denied"**

- Close Arduino IDE Serial Monitor

This project is open source and available under the MIT License.- Check correct COM port in Device Manager (Windows)

- Add user to dialout group (Linux): `sudo usermod -a -G dialout $USER`

---- Try different USB port or cable



**🎉 Your complete Flask vending machine system is ready!****❌ "No response from ESP32"**

- Verify baud rate is 115200

Choose USB serial for easy development and testing, or WiFi for production deployment with multiple devices. The system automatically handles communication and provides comprehensive debugging tools.- Press ESP32 RESET button
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
- **ESP32 Firmware**: `esp32_mock_vend/esp32_mock_vend.ino` / `esp32_wifi_vend/esp32_wifi_vend.ino`

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