#!/bin/bash

# ESP32 Firmware Flashing Tool for Raspberry Pi
# Uses Arduino CLI to flash ESP32 firmware directly from Pi

echo "🔥 ESP32 Firmware Flashing Tool"
echo "========================================================"

# Function to install Arduino CLI
install_arduino_cli() {
    echo "📦 Installing Arduino CLI..."
    
    # Download and install Arduino CLI
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
    sudo mv bin/arduino-cli /usr/local/bin/ 2>/dev/null || true
    
    # Setup Arduino CLI
    arduino-cli core update-index
    arduino-cli core install esp32:esp32
    arduino-cli lib install "ArduinoJson"
    
    echo "✅ Arduino CLI installed and configured"
}

# Function to detect ESP32 devices
detect_esp32() {
    echo "🔍 Scanning for ESP32 devices..."
    ports=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null)
    
    if [ -n "$ports" ]; then
        echo "📱 Found devices:"
        i=1
        for port in $ports; do
            # Try to get device info
            info=$(udevadm info --name=$port 2>/dev/null | grep ID_MODEL || echo "")
            if [ -n "$info" ]; then
                echo "  $i. $port - ${info#*=}"
            else
                echo "  $i. $port - USB Serial Device"
            fi
            i=$((i+1))
        done
        echo "$ports"
    else
        echo "❌ No serial devices found"
        echo "💡 Make sure ESP32 is connected via USB"
        echo "💡 Check if ESP32 drivers are installed"
        return 1
    fi
}

# Function to flash firmware
flash_firmware() {
    local firmware=$1
    local port=$2
    
    echo ""
    echo "🔥 Flashing $firmware to $port..."
    echo "⏳ This may take a few minutes..."
    
    # Copy firmware file if in parent directory
    if [ ! -f "$firmware" ] && [ -f "../$firmware" ]; then
        cp "../$firmware" "./"
        firmware="./$(basename $firmware)"
    fi
    
    if [ ! -f "$firmware" ]; then
        echo "❌ Firmware file not found: $firmware"
        return 1
    fi
    
    # Compile firmware
    echo "🔨 Compiling firmware..."
    arduino-cli compile --fqbn esp32:esp32:esp32 "$firmware"
    
    if [ $? -eq 0 ]; then
        echo "📤 Uploading firmware to ESP32..."
        arduino-cli upload -p "$port" --fqbn esp32:esp32:esp32 "$firmware"
        
        if [ $? -eq 0 ]; then
            echo "✅ ESP32 flashed successfully!"
            echo "🔄 Press RESET button on ESP32 to restart"
            return 0
        else
            echo "❌ Failed to upload firmware"
            echo "💡 Try pressing BOOT button during upload"
            return 1
        fi
    else
        echo "❌ Failed to compile firmware"
        return 1
    fi
}

# Main script
echo "Checking Arduino CLI installation..."

# Check if Arduino CLI is installed
if ! command -v arduino-cli &> /dev/null; then
    echo "⚠️ Arduino CLI not found"
    echo "💡 You can install it using our installation script:"
    echo "   chmod +x install_arduino_cli.sh && ./install_arduino_cli.sh"
    echo ""
    read -p "📦 Install Arduino CLI now? (y/n): " install_choice
    
    if [ "$install_choice" = "y" ] || [ "$install_choice" = "Y" ]; then
        install_arduino_cli
    else
        echo "❌ Arduino CLI required for flashing. Exiting."
        echo "💡 Run ./install_arduino_cli.sh first, then try again"
        exit 1
    fi
else
    echo "✅ Arduino CLI found"
fi

# Detect ESP32 devices
available_ports=$(detect_esp32)
if [ $? -ne 0 ]; then
    exit 1
fi

# Show firmware options
echo ""
echo "🔥 Available firmware files:"
echo "1. ../esp32_mock_vend.ino (USB Serial Communication)"
echo "2. ../esp32_wifi_vend.ino (WiFi Communication)"
echo "3. Exit"
echo ""

# Get firmware choice
read -p "Select firmware to flash (1/2/3): " firmware_choice

case $firmware_choice in
    1)
        firmware="../esp32_mock_vend.ino"
        echo "📝 Selected: USB Serial Communication firmware"
        ;;
    2)
        firmware="../esp32_wifi_vend.ino"
        echo "📝 Selected: WiFi Communication firmware"
        echo "⚠️ IMPORTANT: Update WiFi credentials in the .ino file before flashing!"
        echo "   Edit lines: WIFI_SSID, WIFI_PASSWORD, FLASK_SERVER_IP"
        read -p "Have you updated WiFi credentials? (y/n): " wifi_ready
        if [ "$wifi_ready" != "y" ] && [ "$wifi_ready" != "Y" ]; then
            echo "💡 Please edit ../esp32_wifi_vend.ino and run this script again"
            exit 1
        fi
        ;;
    3)
        echo "👋 Exiting"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

# Get port choice
echo ""
echo "📱 Available ports:"
port_array=($available_ports)
for i in "${!port_array[@]}"; do
    echo "$((i+1)). ${port_array[i]}"
done
echo ""

read -p "Select port (1-${#port_array[@]}): " port_choice

if [ "$port_choice" -ge 1 ] && [ "$port_choice" -le ${#port_array[@]} ]; then
    selected_port=${port_array[$((port_choice-1))]}
    echo "📍 Selected port: $selected_port"
else
    echo "❌ Invalid port choice. Exiting."
    exit 1
fi

# Flash the firmware
flash_firmware "$firmware" "$selected_port"

echo ""
echo "========================================================"
echo "🎉 Flashing complete!"
echo "💡 Next steps:"
echo "1. Press RESET button on ESP32"
echo "2. Open Serial Monitor: arduino-cli monitor -p $selected_port"
echo "3. Or test with: python3 test_system.py"
echo "4. Start Flask server: python3 app.py"
echo "========================================================"