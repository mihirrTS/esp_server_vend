// Raspberry Pi Vending Machine Frontend Logic
document.addEventListener('DOMContentLoaded', function() {
    const vendingButtons = document.querySelectorAll('.vending-button');
    const messageBox = document.getElementById('message');
    const lastActionBox = document.getElementById('last-action');
    const updateNamesButton = document.getElementById('update-names');
    const esp32StatusElement = document.getElementById('esp32-status');
    const communicationModeElement = document.getElementById('communication-mode');
    const serialStatusElement = document.getElementById('serial-status');
    const wifiDevicesElement = document.getElementById('wifi-devices');
    const debugOutputElement = document.getElementById('debug-output');
    
    // Debug buttons
    const testSerialButton = document.getElementById('test-serial');
    const checkDevicesButton = document.getElementById('check-devices');
    const viewHistoryButton = document.getElementById('view-history');
    
    // Initialize slot names from localStorage or defaults
    loadSlotNames();
    
    // Start checking system status
    checkSystemStatus();
    setInterval(checkSystemStatus, 5000); // Check every 5 seconds
    
    // Add click event listeners to vending buttons
    vendingButtons.forEach(button => {
        button.addEventListener('click', function() {
            const slotId = parseInt(this.dataset.slot);
            vendItem(slotId);
        });
    });
    
    // Add event listener for updating slot names
    if (updateNamesButton) {
        updateNamesButton.addEventListener('click', updateSlotNames);
    }
    
    // Debug button event listeners
    if (testSerialButton) {
        testSerialButton.addEventListener('click', testSerialConnection);
    }
    
    if (checkDevicesButton) {
        checkDevicesButton.addEventListener('click', checkAllDevices);
    }
    
    if (viewHistoryButton) {
        viewHistoryButton.addEventListener('click', viewCommandHistory);
    }
    
    /**
     * Send vend request to Flask backend
     */
    async function vendItem(slotId) {
        try {
            // Disable button during request
            const button = document.querySelector(`[data-slot="${slotId}"]`);
            button.disabled = true;
            button.style.opacity = '0.6';
            
            // Update UI
            updateMessage(`🔄 Sending vend command for slot ${slotId}...`, 'loading');
            
            // Send POST request to Flask backend
            const response = await fetch(`/vend/${slotId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Success - show communication method
                const commType = data.communication || 'unknown';
                const commIcon = commType === 'serial' ? '🔌' : commType === 'wifi' ? '📡' : '🖥️';
                
                updateMessage(`✅ ${data.message} (${commIcon} ${commType})`, 'success');
                updateLastAction(`Slot ${slotId} vended via ${commType} at ${new Date().toLocaleTimeString()}`);
                
                // Log to debug output
                logDebug(`VEND SUCCESS: Slot ${slotId} via ${commType}`);
                
                console.log('Vend successful:', data);
            } else {
                // Error from server
                updateMessage(`❌ Error: ${data.message}`, 'error');
                updateLastAction(`Failed to vend slot ${slotId} at ${new Date().toLocaleTimeString()}`);
                logDebug(`VEND ERROR: Slot ${slotId} - ${data.message}`);
                console.error('Vend failed:', data);
            }
            
        } catch (error) {
            // Network or other error
            updateMessage(`❌ Connection error: ${error.message}`, 'error');
            updateLastAction(`Connection error for slot ${slotId} at ${new Date().toLocaleTimeString()}`);
            logDebug(`CONNECTION ERROR: ${error.message}`);
            console.error('Network error:', error);
        } finally {
            // Re-enable button
            const button = document.querySelector(`[data-slot="${slotId}"]`);
            button.disabled = false;
            button.style.opacity = '1';
        }
    }
    
    /**
     * Check system status (enhanced for Raspberry Pi)
     */
    async function checkSystemStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            
            if (response.ok) {
                // Update ESP32 status
                updateESP32Status(data);
                
                // Update communication mode
                updateCommunicationMode(data);
                
                // Update Pi-specific info
                updatePiInfo(data);
            }
        } catch (error) {
            console.warn('Could not check system status:', error);
            updateESP32Status({ esp32_serial: 'disconnected', esp32_wifi_devices: 0 });
        }
    }
    
    /**
     * Update ESP32 status indicator
     */
    function updateESP32Status(data) {
        const serialConnected = data.esp32_serial === 'connected';
        const wifiDevices = data.esp32_wifi_devices || 0;
        const totalConnected = (serialConnected ? 1 : 0) + wifiDevices;
        
        const indicator = esp32StatusElement.querySelector('.status-indicator');
        const statusText = esp32StatusElement.querySelector('.status-text');
        
        if (totalConnected > 0) {
            indicator.className = 'status-indicator online';
            const connections = [];
            if (serialConnected) connections.push('USB');
            if (wifiDevices > 0) connections.push(`${wifiDevices} WiFi`);
            statusText.textContent = `ESP32: ${connections.join(' + ')} connected`;
        } else {
            indicator.className = 'status-indicator offline';
            statusText.textContent = 'ESP32: No devices connected (simulation mode)';
        }
    }
    
    /**
     * Update communication mode indicator
     */
    function updateCommunicationMode(data) {
        const serialConnected = data.esp32_serial === 'connected';
        const wifiDevices = data.esp32_wifi_devices || 0;
        
        const modeText = communicationModeElement.querySelector('.mode-text');
        
        if (serialConnected && wifiDevices > 0) {
            modeText.textContent = 'Communication: Hybrid (USB + WiFi)';
        } else if (serialConnected) {
            modeText.textContent = 'Communication: USB Serial';
        } else if (wifiDevices > 0) {
            modeText.textContent = 'Communication: WiFi Network';
        } else {
            modeText.textContent = 'Communication: Simulation Mode';
        }
    }
    
    /**
     * Update Raspberry Pi specific information
     */
    function updatePiInfo(data) {
        if (serialStatusElement) {
            serialStatusElement.textContent = data.esp32_serial || 'disconnected';
        }
        
        if (wifiDevicesElement) {
            wifiDevicesElement.textContent = data.esp32_wifi_devices || 0;
        }
    }
    
    /**
     * Test serial connection (debug function)
     */
    async function testSerialConnection() {
        logDebug('Testing serial connection...');
        
        try {
            // Send a test command to status endpoint
            const response = await fetch('/status');
            const data = await response.json();
            
            if (data.esp32_serial === 'connected') {
                logDebug('✅ Serial connection: ACTIVE');
                logDebug(`   Port: ${data.communication_modes?.serial || 'unknown'}`);
            } else {
                logDebug('❌ Serial connection: INACTIVE');
                logDebug('   Check USB cable and ESP32 connection');
            }
        } catch (error) {
            logDebug(`❌ Serial test failed: ${error.message}`);
        }
    }
    
    /**
     * Check all devices (debug function)
     */
    async function checkAllDevices() {
        logDebug('Checking all ESP32 devices...');
        
        try {
            const response = await fetch('/esp32/devices');
            const data = await response.json();
            
            logDebug(`Serial devices: ${data.serial_devices?.length || 0}`);
            data.serial_devices?.forEach(device => {
                logDebug(`  ${device.type}: ${device.port} (${device.connected ? 'connected' : 'disconnected'})`);
            });
            
            logDebug(`WiFi devices: ${data.wifi_devices?.length || 0}`);
            data.wifi_devices?.forEach(device => {
                logDebug(`  ${device.device_id}: ${device.ip_address} (${device.status})`);
            });
            
            logDebug(`Total devices: ${data.total_devices}`);
            
        } catch (error) {
            logDebug(`❌ Device check failed: ${error.message}`);
        }
    }
    
    /**
     * View command history (debug function)
     */
    async function viewCommandHistory() {
        logDebug('Fetching command history...');
        
        try {
            const response = await fetch('/esp32/commands/history');
            const data = await response.json();
            
            logDebug(`Command history (last ${data.commands?.length || 0} commands):`);
            
            if (data.commands && data.commands.length > 0) {
                data.commands.forEach(cmd => {
                    const time = new Date(cmd.timestamp).toLocaleTimeString();
                    logDebug(`  [${time}] Slot ${cmd.slot} -> ${cmd.status} (${cmd.device_id})`);
                });
            } else {
                logDebug('  No commands in history');
            }
            
        } catch (error) {
            logDebug(`❌ History fetch failed: ${error.message}`);
        }
    }
    
    /**
     * Log message to debug output
     */
    function logDebug(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logLine = `[${timestamp}] ${message}\n`;
        
        if (debugOutputElement) {
            debugOutputElement.textContent += logLine;
            debugOutputElement.scrollTop = debugOutputElement.scrollHeight;
            
            // Keep only last 50 lines
            const lines = debugOutputElement.textContent.split('\n');
            if (lines.length > 50) {
                debugOutputElement.textContent = lines.slice(-50).join('\n');
            }
        }
        
        console.log(`DEBUG: ${message}`);
    }
    
    /**
     * Update the main message box
     */
    function updateMessage(message, type = 'info') {
        messageBox.textContent = message;
        messageBox.className = `message-box ${type}`;
        
        // Auto-clear success messages after 4 seconds
        if (type === 'success') {
            setTimeout(() => {
                updateMessage('Ready to vend', 'info');
            }, 4000);
        }
    }
    
    /**
     * Update the last action log
     */
    function updateLastAction(action) {
        lastActionBox.textContent = `Last action: ${action}`;
    }
    
    /**
     * Update slot names from input fields
     */
    function updateSlotNames() {
        const slotNames = {};
        
        for (let i = 1; i <= 5; i++) {
            const input = document.getElementById(`slot${i}-name`);
            const customName = input.value.trim();
            
            if (customName) {
                slotNames[i] = customName;
                // Update button label
                const button = document.querySelector(`[data-slot="${i}"]`);
                const slotLabel = button.querySelector('.slot-label');
                slotLabel.textContent = customName;
            } else {
                // Reset to default
                const button = document.querySelector(`[data-slot="${i}"]`);
                const slotLabel = button.querySelector('.slot-label');
                slotLabel.textContent = `Slot ${i}`;
            }
        }
        
        // Save to localStorage
        localStorage.setItem('vendingSlotNames', JSON.stringify(slotNames));
        updateMessage('✅ Slot names updated!', 'success');
        logDebug(`Slot names updated: ${JSON.stringify(slotNames)}`);
    }
    
    /**
     * Load slot names from localStorage
     */
    function loadSlotNames() {
        try {
            const savedNames = localStorage.getItem('vendingSlotNames');
            if (savedNames) {
                const slotNames = JSON.parse(savedNames);
                
                for (const [slotId, name] of Object.entries(slotNames)) {
                    // Update input field
                    const input = document.getElementById(`slot${slotId}-name`);
                    if (input) {
                        input.value = name;
                    }
                    
                    // Update button label
                    const button = document.querySelector(`[data-slot="${slotId}"]`);
                    if (button) {
                        const slotLabel = button.querySelector('.slot-label');
                        slotLabel.textContent = name;
                    }
                }
                
                logDebug(`Loaded slot names: ${JSON.stringify(slotNames)}`);
            }
        } catch (error) {
            console.warn('Could not load saved slot names:', error);
            logDebug(`Failed to load slot names: ${error.message}`);
        }
    }
    
    // Optional: Add keyboard support (1-5 keys)
    document.addEventListener('keydown', function(event) {
        const key = event.key;
        if (key >= '1' && key <= '5') {
            const slotId = parseInt(key);
            vendItem(slotId);
        }
    });
    
    // Initialize debug output
    logDebug('🥧 Raspberry Pi Vending Machine interface loaded');
    logDebug('System ready for ESP32 communication testing');
    
    console.log('🥧 Raspberry Pi Vending Machine interface loaded successfully!');
});