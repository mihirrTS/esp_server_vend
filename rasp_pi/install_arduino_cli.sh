#!/bin/bash

# Arduino CLI Installation Script for Raspberry Pi
# Installs Arduino CLI and sets up ESP32 development environment

echo "🔧 Arduino CLI Installation Script"
echo "========================================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect architecture
detect_architecture() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            echo "Linux_64bit"
            ;;
        aarch64|arm64)
            echo "Linux_ARM64"
            ;;
        armv7l|armv6l)
            echo "Linux_ARMv7"
            ;;
        *)
            echo "Linux_64bit"  # Default fallback
            ;;
    esac
}

# Function to install Arduino CLI
install_arduino_cli() {
    echo "📦 Installing Arduino CLI..."
    
    # Method 1: Try the official installer script
    echo "🔄 Trying official installer..."
    if curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh; then
        # Move to system location
        if [ -f "bin/arduino-cli" ]; then
            echo "📁 Moving Arduino CLI to system location..."
            sudo mv bin/arduino-cli /usr/local/bin/ 2>/dev/null || {
                echo "⚠️ Could not move to /usr/local/bin, trying alternative location..."
                mkdir -p ~/.local/bin
                mv bin/arduino-cli ~/.local/bin/
                export PATH="$HOME/.local/bin:$PATH"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
                echo "✅ Arduino CLI installed to ~/.local/bin"
            }
            rmdir bin 2>/dev/null || true
        fi
    else
        echo "⚠️ Official installer failed, trying manual download..."
        
        # Method 2: Manual download
        local arch=$(detect_architecture)
        local version="latest"
        local download_url="https://github.com/arduino/arduino-cli/releases/latest/download/arduino-cli_${version}_${arch}.tar.gz"
        
        echo "🌐 Downloading Arduino CLI for $arch..."
        
        # Create temporary directory
        local temp_dir=$(mktemp -d)
        cd "$temp_dir"
        
        # Download and extract
        if wget -q "$download_url" -O arduino-cli.tar.gz; then
            tar -xzf arduino-cli.tar.gz
            
            # Install to system or user location
            if sudo mv arduino-cli /usr/local/bin/ 2>/dev/null; then
                echo "✅ Arduino CLI installed to /usr/local/bin"
            else
                mkdir -p ~/.local/bin
                mv arduino-cli ~/.local/bin/
                export PATH="$HOME/.local/bin:$PATH"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
                echo "✅ Arduino CLI installed to ~/.local/bin"
            fi
        else
            echo "❌ Failed to download Arduino CLI"
            cd - > /dev/null
            return 1
        fi
        
        # Cleanup
        cd - > /dev/null
        rm -rf "$temp_dir"
    fi
    
    # Make executable
    sudo chmod +x /usr/local/bin/arduino-cli 2>/dev/null || chmod +x ~/.local/bin/arduino-cli
    
    return 0
}

# Function to setup ESP32 environment
setup_esp32_environment() {
    echo ""
    echo "🔧 Setting up ESP32 development environment..."
    
    # Initialize Arduino CLI
    echo "🔄 Initializing Arduino CLI..."
    arduino-cli config init
    
    # Update core index
    echo "📦 Updating package index..."
    arduino-cli core update-index
    
    # Install ESP32 core
    echo "📱 Installing ESP32 core..."
    arduino-cli core install esp32:esp32
    
    if [ $? -eq 0 ]; then
        echo "✅ ESP32 core installed successfully"
    else
        echo "❌ Failed to install ESP32 core"
        return 1
    fi
    
    # Install required libraries
    echo "📚 Installing required libraries..."
    arduino-cli lib install "ArduinoJson"
    
    if [ $? -eq 0 ]; then
        echo "✅ ArduinoJson library installed successfully"
    else
        echo "⚠️ Failed to install ArduinoJson library"
        echo "💡 You can install it later with: arduino-cli lib install \"ArduinoJson\""
    fi
    
    return 0
}

# Function to verify installation
verify_installation() {
    echo ""
    echo "🔍 Verifying installation..."
    
    if command_exists arduino-cli; then
        local version=$(arduino-cli version)
        echo "✅ Arduino CLI installed: $version"
        
        # Check ESP32 core
        if arduino-cli core list | grep -q "esp32:esp32"; then
            echo "✅ ESP32 core available"
        else
            echo "⚠️ ESP32 core not found"
            return 1
        fi
        
        # Check ArduinoJson library
        if arduino-cli lib list | grep -q "ArduinoJson"; then
            echo "✅ ArduinoJson library available"
        else
            echo "⚠️ ArduinoJson library not found"
        fi
        
        # List connected boards
        echo ""
        echo "🔌 Scanning for connected boards..."
        arduino-cli board list
        
        return 0
    else
        echo "❌ Arduino CLI not found in PATH"
        return 1
    fi
}

# Function to show usage examples
show_usage_examples() {
    echo ""
    echo "🎯 Usage Examples:"
    echo "========================================================"
    echo ""
    echo "📋 List available boards:"
    echo "arduino-cli board listall esp32"
    echo ""
    echo "🔌 Detect connected boards:"
    echo "arduino-cli board list"
    echo ""
    echo "🔨 Compile ESP32 sketch:"
    echo "arduino-cli compile --fqbn esp32:esp32:esp32 sketch.ino"
    echo ""
    echo "📤 Upload to ESP32:"
    echo "arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 sketch.ino"
    echo ""
    echo "📡 Monitor serial output:"
    echo "arduino-cli monitor -p /dev/ttyUSB0"
    echo ""
    echo "📚 Install additional libraries:"
    echo "arduino-cli lib search wifi"
    echo "arduino-cli lib install \"WiFi\""
    echo ""
    echo "🔄 Update cores and libraries:"
    echo "arduino-cli core update-index"
    echo "arduino-cli core upgrade"
    echo "arduino-cli lib upgrade"
}

# Main installation process
echo "Starting Arduino CLI installation for ESP32 development..."
echo ""

# Check if already installed
if command_exists arduino-cli; then
    echo "✅ Arduino CLI already installed"
    arduino-cli version
    echo ""
    read -p "🔄 Reinstall Arduino CLI? (y/n): " reinstall
    if [ "$reinstall" != "y" ] && [ "$reinstall" != "Y" ]; then
        echo "ℹ️ Skipping Arduino CLI installation"
        
        # Still setup ESP32 environment
        read -p "🔧 Setup/update ESP32 environment? (y/n): " setup_esp32
        if [ "$setup_esp32" = "y" ] || [ "$setup_esp32" = "Y" ]; then
            setup_esp32_environment
        fi
        
        verify_installation
        show_usage_examples
        exit 0
    fi
fi

# Check dependencies
echo "🔍 Checking dependencies..."

# Check for curl or wget
if ! command_exists curl && ! command_exists wget; then
    echo "❌ Neither curl nor wget found. Installing wget..."
    sudo apt update && sudo apt install -y wget curl
fi

# Check for tar
if ! command_exists tar; then
    echo "❌ tar not found. Installing..."
    sudo apt update && sudo apt install -y tar
fi

echo "✅ Dependencies satisfied"
echo ""

# Install Arduino CLI
install_arduino_cli

if [ $? -eq 0 ]; then
    echo "✅ Arduino CLI installation completed"
else
    echo "❌ Arduino CLI installation failed"
    echo ""
    echo "🔧 Manual installation options:"
    echo "1. Using package manager:"
    echo "   curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh"
    echo ""
    echo "2. Download binary directly:"
    echo "   https://github.com/arduino/arduino-cli/releases"
    echo ""
    exit 1
fi

# Setup ESP32 environment
setup_esp32_environment

if [ $? -eq 0 ]; then
    echo "✅ ESP32 environment setup completed"
else
    echo "⚠️ ESP32 environment setup had issues"
fi

# Verify installation
verify_installation

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation completed successfully!"
    show_usage_examples
    echo ""
    echo "💡 Next steps:"
    echo "1. Connect ESP32 via USB"
    echo "2. Use ./flash_esp32.sh to flash firmware"
    echo "3. Or compile manually with examples above"
else
    echo ""
    echo "⚠️ Installation completed with warnings"
    echo "💡 Try running the verification manually:"
    echo "arduino-cli version"
    echo "arduino-cli core list"
fi

echo ""
echo "========================================================"
echo "🔧 Arduino CLI setup complete!"
echo "========================================================"