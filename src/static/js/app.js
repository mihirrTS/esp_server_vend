// Vending Machine Frontend Logic
document.addEventListener('DOMContentLoaded', function() {
    const vendingButtons = document.querySelectorAll('.vending-button');
    const messageBox = document.getElementById('message');
    const lastActionBox = document.getElementById('last-action');
    const updateNamesButton = document.getElementById('update-names');
    const esp32StatusElement = document.getElementById('esp32-status');
    
    // Connection management elements
    const scanPortsButton = document.getElementById('scan-ports');
    const portSelect = document.getElementById('port-select');
    const connectSerialButton = document.getElementById('connect-serial');
    const disconnectSerialButton = document.getElementById('disconnect-serial');
    const serialStatusElement = document.getElementById('serial-status');
    const wifiDevicesElement = document.getElementById('wifi-devices');
    const currentModeElement = document.getElementById('current-mode');
    
    // Monitor elements
    const startMonitorButton = document.getElementById('start-monitor');
    const stopMonitorButton = document.getElementById('stop-monitor');
    const clearLogButton = document.getElementById('clear-log');
    const sendTestButton = document.getElementById('send-test');
    const addTestDataButton = document.getElementById('add-test-data');
    const monitorStatusElement = document.getElementById('monitor-status');
    const logCountElement = document.getElementById('log-count');
    const communicationLogElement = document.getElementById('communication-log');
    const monitorStatusDisplay = document.getElementById('monitor-status-display');
    
    // Device selection elements
    const deviceListElement = document.getElementById('device-list');
    const activeDeviceDisplay = document.getElementById('active-device-display');
    const refreshDevicesButton = document.getElementById('refresh-devices');
    const autoSelectDeviceButton = document.getElementById('auto-select-device');
    
    // Monitor state
    let isMonitoring = false;
    let monitorInterval = null;
    let lastLogCount = 0;
    let selectedDevice = null;
    
    // Initialize
    loadSlotNames();
    checkESP32Status();
    checkCommunicationMode();
    
    // Auto-refresh status
    setInterval(checkESP32Status, 10000); // Check every 10 seconds
    setInterval(checkCommunicationMode, 5000); // Check mode every 5 seconds
    setInterval(refreshDeviceList, 8000); // Refresh devices every 8 seconds
    
    // Initial device list load
    refreshDeviceList();
    
    // Add event listeners
    vendingButtons.forEach(button => {
        button.addEventListener('click', function() {
            const slotId = parseInt(this.dataset.slot);
            vendItem(slotId);
        });
    });
    
    if (updateNamesButton) {
        updateNamesButton.addEventListener('click', updateSlotNames);
    }
    
    // Connection management event listeners
    if (scanPortsButton) {
        scanPortsButton.addEventListener('click', scanSerialPorts);
    }
    
    if (connectSerialButton) {
        connectSerialButton.addEventListener('click', connectSerial);
    }
    
    if (disconnectSerialButton) {
        disconnectSerialButton.addEventListener('click', disconnectSerial);
    }
    
    if (portSelect) {
        portSelect.addEventListener('change', function() {
            connectSerialButton.disabled = !this.value;
        });
    }
    
    // Monitor event listeners
    if (startMonitorButton) {
        startMonitorButton.addEventListener('click', startMonitoring);
    }
    
    if (stopMonitorButton) {
        stopMonitorButton.addEventListener('click', stopMonitoring);
    }
    
    if (clearLogButton) {
        clearLogButton.addEventListener('click', clearCommunicationLog);
    }
    
    if (sendTestButton) {
        sendTestButton.addEventListener('click', sendTestCommands);
    }
    
    if (addTestDataButton) {
        addTestDataButton.addEventListener('click', addTestData);
    }
    
    // Device management event listeners
    if (refreshDevicesButton) {
        refreshDevicesButton.addEventListener('click', refreshDeviceList);
    }
    
    if (autoSelectDeviceButton) {
        autoSelectDeviceButton.addEventListener('click', autoSelectDevice);
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
                // Success
                updateMessage(`✅ ${data.message}`, 'success');
                updateLastAction(`Slot ${slotId} vended successfully at ${new Date().toLocaleTimeString()}`);
                console.log('Vend successful:', data);
            } else {
                // Error from server
                updateMessage(`❌ Error: ${data.message}`, 'error');
                updateLastAction(`Failed to vend slot ${slotId} at ${new Date().toLocaleTimeString()}`);
                console.error('Vend failed:', data);
            }
            
        } catch (error) {
            // Network or other error
            updateMessage(`❌ Connection error: ${error.message}`, 'error');
            updateLastAction(`Connection error for slot ${slotId} at ${new Date().toLocaleTimeString()}`);
            console.error('Network error:', error);
        } finally {
            // Re-enable button
            const button = document.querySelector(`[data-slot="${slotId}"]`);
            button.disabled = false;
            button.style.opacity = '1';
        }
    }
    
    /**
     * Update the main message box
     */
    function updateMessage(message, type = 'info') {
        messageBox.textContent = message;
        messageBox.className = `message-box ${type}`;
        
        // Auto-clear success messages after 3 seconds
        if (type === 'success') {
            setTimeout(() => {
                updateMessage('Ready to vend', 'info');
            }, 3000);
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
            }
        } catch (error) {
            console.warn('Could not load saved slot names:', error);
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
    
    /**
     * Check ESP32 device status
     */
    async function checkESP32Status() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            
            if (response.ok) {
                const onlineDevices = data.online_devices || 0;
                const totalDevices = data.esp32_devices || 0;
                
                const indicator = esp32StatusElement.querySelector('.status-indicator');
                const statusText = esp32StatusElement.querySelector('.status-text');
                
                if (onlineDevices > 0) {
                    indicator.className = 'status-indicator online';
                    statusText.textContent = `ESP32: ${onlineDevices} device(s) connected`;
                } else if (totalDevices > 0) {
                    indicator.className = 'status-indicator offline';
                    statusText.textContent = `ESP32: ${totalDevices} device(s) registered (offline)`;
                } else {
                    indicator.className = 'status-indicator offline';
                    statusText.textContent = 'ESP32: No devices connected (simulation mode)';
                }
                
                // Update connection status displays
                updateConnectionDisplays(data);
            }
        } catch (error) {
            console.warn('Could not check ESP32 status:', error);
            const indicator = esp32StatusElement.querySelector('.status-indicator');
            const statusText = esp32StatusElement.querySelector('.status-text');
            indicator.className = 'status-indicator offline';
            statusText.textContent = 'ESP32: Connection check failed';
        }
    }
    
    /**
     * Update connection displays based on status data
     */
    function updateConnectionDisplays(statusData) {
        // Update serial status
        if (serialStatusElement && statusData.communication_modes) {
            const serialMode = statusData.communication_modes.serial;
            if (serialMode.status === 'connected') {
                serialStatusElement.textContent = `Connected to ${serialMode.port}`;
                serialStatusElement.className = 'connection-status connected';
                disconnectSerialButton.disabled = false;
                connectSerialButton.disabled = true;
            } else {
                serialStatusElement.textContent = 'Not connected';
                serialStatusElement.className = 'connection-status disconnected';
                disconnectSerialButton.disabled = true;
                connectSerialButton.disabled = !portSelect.value;
            }
        }
        
        // Update WiFi devices
        if (wifiDevicesElement) {
            const wifiDevices = statusData.esp32_wifi_devices || 0;
            if (wifiDevices > 0) {
                wifiDevicesElement.innerHTML = `<span class="status-text">${wifiDevices} WiFi device(s) connected</span>`;
                wifiDevicesElement.className = 'wifi-status active';
            } else {
                wifiDevicesElement.innerHTML = '<span class="status-text">No WiFi devices detected</span>';
                wifiDevicesElement.className = 'wifi-status';
            }
        }
    }
    
    /**
     * Check current communication mode
     */
    async function checkCommunicationMode() {
        try {
            const response = await fetch('/esp32/communication/mode');
            const data = await response.json();
            
            if (response.ok && currentModeElement) {
                currentModeElement.textContent = data.current_mode || 'Unknown';
            }
        } catch (error) {
            console.warn('Could not check communication mode:', error);
        }
    }
    
    /**
     * Scan for available serial ports
     */
    async function scanSerialPorts() {
        try {
            scanPortsButton.disabled = true;
            scanPortsButton.textContent = '🔍 Scanning...';
            
            const response = await fetch('/esp32/serial/scan');
            const data = await response.json();
            
            if (response.ok) {
                // Clear existing options
                portSelect.innerHTML = '<option value="">Select a port...</option>';
                
                // Add scanned ports
                data.ports.forEach(port => {
                    const option = document.createElement('option');
                    option.value = port.device;
                    
                    let displayText = `${port.device} - ${port.description}`;
                    if (port.likely_esp32) {
                        displayText += ' (likely ESP32)';
                    }
                    if (!port.available) {
                        displayText += ' [IN USE - close other programs]';
                        option.disabled = true;
                        option.style.color = '#999';
                    }
                    
                    option.textContent = displayText;
                    portSelect.appendChild(option);
                });
                
                portSelect.disabled = false;
                updateMessage(`✅ Found ${data.ports.length} serial ports`, 'success');
            } else {
                updateMessage(`❌ Error scanning ports: ${data.error}`, 'error');
            }
        } catch (error) {
            updateMessage(`❌ Error scanning ports: ${error.message}`, 'error');
        } finally {
            scanPortsButton.disabled = false;
            scanPortsButton.textContent = '🔍 Scan Ports';
        }
    }
    
    /**
     * Connect to ESP32 via serial
     */
    async function connectSerial() {
        try {
            const selectedPort = portSelect.value;
            if (!selectedPort) {
                updateMessage('❌ Please select a port first', 'error');
                return;
            }
            
            // Update button state
            connectSerialButton.disabled = true;
            connectSerialButton.textContent = '📱 Connecting...';
            
            const response = await fetch('/esp32/serial/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ port: selectedPort })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                updateMessage(`✅ ${data.message}`, 'success');
                // Update button to show connected state
                connectSerialButton.textContent = '✅ Connected';
                connectSerialButton.disabled = true;
                disconnectSerialButton.disabled = false;
                checkESP32Status(); // Refresh status
            } else {
                updateMessage(`❌ ${data.message}`, 'error');
                // Reset button state on failure
                connectSerialButton.disabled = false;
                connectSerialButton.textContent = '📱 Connect';
            }
        } catch (error) {
            updateMessage(`❌ Connection error: ${error.message}`, 'error');
            // Reset button state on error
            connectSerialButton.disabled = false;
            connectSerialButton.textContent = '📱 Connect';
        }
    }
    
    /**
     * Disconnect ESP32 serial connection
     */
    async function disconnectSerial() {
        try {
            disconnectSerialButton.disabled = true;
            disconnectSerialButton.textContent = '🔌 Disconnecting...';
            
            const response = await fetch('/esp32/serial/disconnect', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                updateMessage(`✅ ${data.message}`, 'success');
                // Reset button states
                disconnectSerialButton.disabled = true;
                disconnectSerialButton.textContent = '🔌 Disconnect';
                connectSerialButton.disabled = false;
                connectSerialButton.textContent = '📱 Connect';
                checkESP32Status(); // Refresh status
            } else {
                updateMessage(`❌ Error: ${data.error}`, 'error');
                disconnectSerialButton.disabled = false;
                disconnectSerialButton.textContent = '🔌 Disconnect';
            }
        } catch (error) {
            updateMessage(`❌ Disconnect error: ${error.message}`, 'error');
            disconnectSerialButton.disabled = false;
            disconnectSerialButton.textContent = '🔌 Disconnect';
        }
    }
    
    /**
     * Start monitoring ESP32 communication
     */
    function startMonitoring() {
        if (isMonitoring) return;
        
        isMonitoring = true;
        startMonitorButton.disabled = true;
        stopMonitorButton.disabled = false;
        monitorStatusElement.textContent = 'Monitor running';
        monitorStatusElement.className = 'monitor-status active';
        
        // Update status display
        if (monitorStatusDisplay) {
            const indicator = monitorStatusDisplay.querySelector('.status-indicator');
            const statusText = monitorStatusDisplay.querySelector('.status-text');
            indicator.className = 'status-indicator online';
            statusText.textContent = 'Monitor: Running';
        }
        
        // Clear placeholder
        communicationLogElement.innerHTML = '';
        
        // Start polling for communication log
        monitorInterval = setInterval(updateCommunicationLog, 500); // Check every 500ms
        
        updateMessage('✅ ESP32 communication monitor started', 'success');
    }
    
    /**
     * Stop monitoring ESP32 communication
     */
    function stopMonitoring() {
        if (!isMonitoring) return;
        
        isMonitoring = false;
        startMonitorButton.disabled = false;
        stopMonitorButton.disabled = true;
        monitorStatusElement.textContent = 'Monitor stopped';
        monitorStatusElement.className = 'monitor-status';
        
        // Update status display
        if (monitorStatusDisplay) {
            const indicator = monitorStatusDisplay.querySelector('.status-indicator');
            const statusText = monitorStatusDisplay.querySelector('.status-text');
            indicator.className = 'status-indicator offline';
            statusText.textContent = 'Monitor: Stopped';
        }
        
        if (monitorInterval) {
            clearInterval(monitorInterval);
            monitorInterval = null;
        }
        
        updateMessage('🛑 ESP32 communication monitor stopped', 'info');
    }
    
    /**
     * Update communication log from server
     */
    async function updateCommunicationLog() {
        try {
            const response = await fetch('/esp32/communication/log');
            const data = await response.json();
            
            if (response.ok) {
                const logEntries = data.log_entries || [];
                const totalEntries = data.total_entries || 0;
                
                // Update log count
                logCountElement.textContent = `${totalEntries} messages`;
                
                // Show only new entries
                if (logEntries.length > lastLogCount) {
                    const newEntries = logEntries.slice(lastLogCount);
                    
                    newEntries.forEach(entry => {
                        addLogEntry(entry);
                    });
                    
                    lastLogCount = logEntries.length;
                    
                    // Auto-scroll to bottom
                    communicationLogElement.scrollTop = communicationLogElement.scrollHeight;
                }
            }
        } catch (error) {
            console.warn('Could not update communication log:', error);
        }
    }
    
    /**
     * Add a log entry to the display
     */
    function addLogEntry(entry) {
        const logDiv = document.createElement('div');
        logDiv.className = `log-entry ${entry.direction} ${entry.type}`;
        
        const timestamp = entry.formatted_time || new Date().toLocaleTimeString();
        const direction = entry.direction === 'sent' ? 'SENT' : 'RECV';
        const message = entry.message || '';
        const deviceId = entry.device_id || 'unknown';
        const deviceType = entry.device_type || 'unknown';
        
        // Get appropriate icon based on type and direction
        let icon = '';
        if (entry.direction === 'sent') {
            icon = '📤';
        } else if (entry.direction === 'received') {
            if (entry.type === 'vend') icon = '🏪';
            else if (entry.type === 'status') icon = '📊';
            else if (entry.type === 'error') icon = '❌';
            else if (entry.type === 'success') icon = '✅';
            else if (entry.type === 'discovery') icon = '🔍';
            else icon = '📥';
        } else {
            icon = 'ℹ️';
        }
        
        // Device type icon
        const deviceIcon = deviceType === 'serial' ? '🔌' : deviceType === 'wifi' ? '📶' : '❓';
        
        logDiv.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-direction">${icon} ${direction}:</span>
            <span class="log-device">${deviceIcon} ${deviceId}:</span>
            <span class="log-message">${message}</span>
        `;
        
        communicationLogElement.appendChild(logDiv);
        
        // Keep only last 100 entries to prevent memory issues
        const entries = communicationLogElement.children;
        if (entries.length > 100) {
            communicationLogElement.removeChild(entries[0]);
        }
    }
    
    /**
     * Clear communication log
     */
    async function clearCommunicationLog() {
        try {
            const response = await fetch('/esp32/communication/log/clear', {
                method: 'POST'
            });
            
            if (response.ok) {
                communicationLogElement.innerHTML = '<div class="log-placeholder">Communication log cleared</div>';
                lastLogCount = 0;
                logCountElement.textContent = '0 messages';
                updateMessage('✅ Communication log cleared', 'success');
            } else {
                updateMessage('❌ Failed to clear log', 'error');
            }
        } catch (error) {
            updateMessage(`❌ Error clearing log: ${error.message}`, 'error');
        }
    }
    
    /**
     * Send test commands to ESP32
     */
    async function sendTestCommands() {
        const testSlots = [1, 2, 3];
        
        updateMessage('🧪 Sending test commands to ESP32...', 'info');
        
        for (const slot of testSlots) {
            try {
                const response = await fetch(`/vend/${slot}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    console.log(`✅ Test slot ${slot}: ${data.message}`);
                } else {
                    console.log(`❌ Test slot ${slot} failed: ${data.message}`);
                }
                
                // Wait between commands
                await new Promise(resolve => setTimeout(resolve, 1000));
                
            } catch (error) {
                console.log(`❌ Test slot ${slot} error: ${error.message}`);
            }
        }
        
        updateMessage('✅ Test commands completed', 'success');
    }
    
    /**
     * Add test data to communication log for demonstration
     */
    async function addTestData() {
        try {
            const response = await fetch('/esp32/communication/test', {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                updateMessage(`✅ Added ${data.entries_added} test entries to log`, 'success');
                
                // If monitoring is active, the new entries will appear automatically
                if (!isMonitoring) {
                    updateMessage('💡 Start monitor to see the test entries', 'info');
                }
            } else {
                updateMessage('❌ Failed to add test data', 'error');
            }
        } catch (error) {
            updateMessage(`❌ Error adding test data: ${error.message}`, 'error');
        }
    }
    
    // =================================
    // Device Management Functions
    // =================================
    
    /**
     * Refresh the list of available devices
     */
    async function refreshDeviceList() {
        try {
            const response = await fetch('/esp32/devices/list');
            const data = await response.json();
            
            if (response.ok) {
                displayDeviceList(data.devices);
                updateActiveDeviceDisplay(data.active_device);
            }
        } catch (error) {
            console.warn('Could not refresh device list:', error);
        }
    }
    
    /**
     * Display the list of devices
     */
    function displayDeviceList(devices) {
        if (!deviceListElement) return;
        
        if (devices.length === 0) {
            deviceListElement.innerHTML = '<div class="device-placeholder">No devices detected</div>';
            return;
        }
        
        deviceListElement.innerHTML = '';
        
        devices.forEach(device => {
            const deviceDiv = document.createElement('div');
            deviceDiv.className = `device-item ${device.connected ? 'connected' : 'disconnected'}`;
            if (selectedDevice === device.device_id) {
                deviceDiv.className += ' selected';
            }
            
            const deviceType = device.type;
            const deviceName = device.type === 'serial' ? 
                `Serial ${device.port}` : 
                `WiFi ${device.device_id}`;
            
            const statusText = device.connected ? 'Connected' : 'Disconnected';
            const additionalInfo = device.type === 'serial' ? 
                device.port : 
                device.ip_address || 'No IP';
            
            deviceDiv.innerHTML = `
                <div class="device-status-indicator ${device.connected ? 'connected' : ''}"></div>
                <div class="device-header">
                    <span class="device-name">${deviceName}</span>
                    <span class="device-type ${deviceType}">${deviceType.toUpperCase()}</span>
                </div>
                <div class="device-info">${additionalInfo} - ${statusText}</div>
            `;
            
            // Add click handler for device selection
            if (device.connected) {
                deviceDiv.addEventListener('click', () => selectDevice(device.device_id));
            }
            
            deviceListElement.appendChild(deviceDiv);
        });
    }
    
    /**
     * Select a specific device
     */
    async function selectDevice(deviceId) {
        try {
            const response = await fetch('/esp32/devices/select', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ device_id: deviceId })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                selectedDevice = deviceId;
                updateMessage(`✅ Selected device: ${deviceId}`, 'success');
                refreshDeviceList(); // Refresh to show selection
                updateActiveDeviceDisplay(deviceId);
            } else {
                updateMessage(`❌ Failed to select device: ${data.error}`, 'error');
            }
        } catch (error) {
            updateMessage(`❌ Error selecting device: ${error.message}`, 'error');
        }
    }
    
    /**
     * Auto-select best available device
     */
    async function autoSelectDevice() {
        try {
            const response = await fetch('/esp32/devices/auto-select', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                selectedDevice = data.active_device;
                updateMessage(`✅ ${data.message}`, 'success');
                refreshDeviceList();
                updateActiveDeviceDisplay(data.active_device);
            } else {
                updateMessage(`❌ Auto-select failed: ${data.error}`, 'error');
            }
        } catch (error) {
            updateMessage(`❌ Error with auto-select: ${error.message}`, 'error');
        }
    }
    
    /**
     * Update active device display
     */
    function updateActiveDeviceDisplay(activeDevice) {
        if (!activeDeviceDisplay) return;
        
        const statusSpan = activeDeviceDisplay.querySelector('.device-status');
        
        if (activeDevice) {
            const deviceType = activeDevice.startsWith('serial_') ? 'Serial' : 'WiFi';
            const deviceName = activeDevice.replace('serial_', '').replace('wifi_', '');
            statusSpan.textContent = `🎯 ${deviceType}: ${deviceName}`;
            statusSpan.style.color = '#27ae60';
        } else {
            statusSpan.textContent = 'Auto-select (priority: Serial → WiFi)';
            statusSpan.style.color = '#95a5a6';
        }
    }
    
    console.log('Vending Machine interface loaded successfully!');
});