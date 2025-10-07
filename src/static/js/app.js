// Vending Machine Frontend Logic
document.addEventListener('DOMContentLoaded', function() {
    const vendingButtons = document.querySelectorAll('.vending-button');
    const messageBox = document.getElementById('message');
    const lastActionBox = document.getElementById('last-action');
    const updateNamesButton = document.getElementById('update-names');
    const esp32StatusElement = document.getElementById('esp32-status');
    
    // Initialize slot names from localStorage or defaults
    loadSlotNames();
    
    // Start checking ESP32 status
    checkESP32Status();
    setInterval(checkESP32Status, 10000); // Check every 10 seconds
    
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
            }
        } catch (error) {
            console.warn('Could not check ESP32 status:', error);
            const indicator = esp32StatusElement.querySelector('.status-indicator');
            const statusText = esp32StatusElement.querySelector('.status-text');
            indicator.className = 'status-indicator offline';
            statusText.textContent = 'ESP32: Connection check failed';
        }
    }
    
    console.log('Vending Machine interface loaded successfully!');
});