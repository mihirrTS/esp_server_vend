/*
 * ESP32 Mock Vending Machine Firmware
 * 
 * This Arduino sketch simulates receiving vending commands from Flask server.
 * Later this can be extended to control actual stepper motors/servos for vending.
 * 
 * Commands expected: VEND:1, VEND:2, VEND:3, VEND:4, VEND:5
 * 
 * Hardware Requirements:
 * - ESP32 development board
 * - USB cable for programming/power
 * 
 * Optional (for future hardware integration):
 * - 5x Stepper motors or servos
 * - Motor driver boards
 * - Power supply
 * - Sensors for slot detection
 */

// Pin definitions (for future hardware expansion)
#define SLOT_1_PIN 2
#define SLOT_2_PIN 4
#define SLOT_3_PIN 5
#define SLOT_4_PIN 18
#define SLOT_5_PIN 19

// Status LED pin (built-in LED on most ESP32 boards)
#define STATUS_LED_PIN 2

// Serial communication settings
#define SERIAL_BAUD_RATE 115200
#define COMMAND_TIMEOUT 3000  // 3 seconds timeout for faster response
#define RESPONSE_DELAY 100    // Faster response delay

// Global variables
String inputBuffer = "";
unsigned long lastCommandTime = 0;
unsigned long lastHeartbeat = 0;
bool systemReady = true;

void setup() {
  // Initialize Serial communication
  Serial.begin(SERIAL_BAUD_RATE);
  delay(1000);  // Give serial time to initialize
  
  // Initialize pins (for future hardware)
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(SLOT_1_PIN, OUTPUT);
  pinMode(SLOT_2_PIN, OUTPUT);
  pinMode(SLOT_3_PIN, OUTPUT);
  pinMode(SLOT_4_PIN, OUTPUT);
  pinMode(SLOT_5_PIN, OUTPUT);
  
  // Set all pins to LOW initially
  digitalWrite(STATUS_LED_PIN, LOW);
  digitalWrite(SLOT_1_PIN, LOW);
  digitalWrite(SLOT_2_PIN, LOW);
  digitalWrite(SLOT_3_PIN, LOW);
  digitalWrite(SLOT_4_PIN, LOW);
  digitalWrite(SLOT_5_PIN, LOW);
  
  // Startup sequence with enhanced identification
  Serial.println("========================================");
  Serial.println("ESP32 USB Serial Vending Machine v1.1");
  Serial.println("========================================");
  Serial.println("System initializing...");
  delay(300);  // Faster startup
  
  // Send identification string for auto-discovery
  Serial.println("DEVICE_ID:ESP32_USB_VENDING");
  Serial.println("DEVICE_TYPE:VENDING_MACHINE");
  Serial.println("COMM_METHOD:USB_SERIAL");
  Serial.println("FIRMWARE_VERSION:1.1");
  Serial.println("SLOTS_AVAILABLE:5");
  
  // Blink status LED to show system is ready (faster sequence)
  for (int i = 0; i < 2; i++) {  // Fewer blinks for faster startup
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(150);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(150);
  }
  
  Serial.println("✅ System ready!");
  Serial.println("📡 Auto-discovery enabled");
  Serial.println("⚡ Fast response mode active");
  Serial.println("Waiting for commands from Flask server...");
  Serial.println("Expected format: VEND:1, VEND:2, VEND:3, VEND:4, VEND:5");
  Serial.println("========================================");
  
  lastCommandTime = millis();
}

void loop() {
  // Check for incoming serial data (optimized for speed)
  while (Serial.available() > 0) {
    char receivedChar = Serial.read();
    
    // Build command string until newline
    if (receivedChar == '\n' || receivedChar == '\r') {
      if (inputBuffer.length() > 0) {
        processCommand(inputBuffer);
        inputBuffer = "";  // Clear buffer
      }
    } else {
      inputBuffer += receivedChar;
      
      // Prevent buffer overflow
      if (inputBuffer.length() > 50) {
        Serial.println("❌ Error: Command too long, clearing buffer");
        inputBuffer = "";
      }
    }
    
    lastCommandTime = millis();
  }
  
  // Heartbeat/status indicator (optimized timing)
  if (millis() - lastHeartbeat > 1500) {  // Faster heartbeat for better feedback
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);  // Longer blink for visibility
    digitalWrite(STATUS_LED_PIN, LOW);
    lastHeartbeat = millis();
  }
  
  // Optional: Add watchdog functionality
  if (millis() - lastCommandTime > 30000) {  // 30 seconds without activity
    static unsigned long lastStatusMessage = 0;
    if (millis() - lastStatusMessage > 10000) {  // Print status every 10 seconds
      Serial.println("💤 System idle - waiting for commands...");
      lastStatusMessage = millis();
    }
  }
  
  delay(10);  // Small delay to prevent overwhelming the CPU
}

void processCommand(String command) {
  command.trim();  // Remove whitespace
  command.toUpperCase();  // Convert to uppercase for consistency
  
  Serial.println("📨 Received command: " + command);
  
  // Parse VEND commands
  if (command.startsWith("VEND:")) {
    String slotStr = command.substring(5);  // Get slot number after "VEND:"
    int slotNumber = slotStr.toInt();
    
    if (slotNumber >= 1 && slotNumber <= 5) {
      vendSlot(slotNumber);
    } else {
      Serial.println("❌ Error: Invalid slot number. Must be 1-5");
      Serial.println("📝 Usage: VEND:1, VEND:2, VEND:3, VEND:4, or VEND:5");
    }
  }
  // Enhanced discovery and status commands
  else if (command == "DISCOVER" || command == "IDENTIFY") {
    Serial.println("DEVICE_RESPONSE:ESP32_USB_VENDING");
    Serial.println("DEVICE_ID:ESP32_USB_" + String(ESP.getEfuseMac(), HEX));
    Serial.println("DEVICE_TYPE:VENDING_MACHINE");
    Serial.println("COMM_METHOD:USB_SERIAL");
    Serial.println("FIRMWARE_VERSION:1.1");
    Serial.println("SLOTS_AVAILABLE:5");
    Serial.println("STATUS:READY");
  }
  // Handle status/ping commands with enhanced info
  else if (command == "STATUS" || command == "PING") {
    Serial.println("✅ STATUS:ONLINE");
    Serial.println("📊 SLOTS:5");
    Serial.println("🔋 READY:TRUE");
    Serial.println("⚡ FAST_MODE:ENABLED");
    Serial.println("� UPTIME:" + String(millis() / 1000) + "s");
  }
  // Quick response command for speed testing
  else if (command == "QUICK" || command == "FAST") {
    Serial.println("⚡ QUICK_RESPONSE:OK");
  }
  // Handle reset command
  else if (command == "RESET") {
    Serial.println("🔄 Resetting system...");
    delay(300);  // Faster reset
    ESP.restart();
  }
  // Handle help command
  else if (command == "HELP") {
    printHelp();
  }
  // Unknown command
  else {
    Serial.println("❌ Error: Unknown command '" + command + "'");
    Serial.println("💡 Type 'HELP' for available commands");
  }
  
  Serial.println("----------------------------------------");
}

void vendSlot(int slotNumber) {
  if (!systemReady) {
    Serial.println("❌ Error: System not ready for vending");
    return;
  }
  
  systemReady = false;  // Prevent concurrent operations
  digitalWrite(STATUS_LED_PIN, HIGH);  // Turn on status LED during operation
  
  Serial.println("🎯 Vending from slot " + String(slotNumber) + "...");
  
  // Immediate success response for better user experience
  Serial.println("✅ VEND_SUCCESS:" + String(slotNumber));
  
  // Simulate motor activation sequence (optimized for speed)
  int motorPin = getMotorPin(slotNumber);
  
  // Step 1: Activate motor (faster simulation)
  Serial.println("⚡ Activating motor for slot " + String(slotNumber));
  digitalWrite(motorPin, HIGH);
  delay(RESPONSE_DELAY);  // Faster response
  
  // Step 2: Quick dispense simulation
  Serial.println("📦 Item dispensed from slot " + String(slotNumber));
  Serial.println("💰 Transaction complete!");
  
  // Quick success indicator
  for (int i = 0; i < 2; i++) {  // Fewer blinks for speed
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(RESPONSE_DELAY);
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(RESPONSE_DELAY);
  }
  
  // Step 3: Deactivate motor
  digitalWrite(motorPin, LOW);
  Serial.println("🛑 Motor deactivated");
  
  // Step 4: Update status
  digitalWrite(STATUS_LED_PIN, LOW);
  systemReady = true;
  
  Serial.println("✨ Vending operation completed for slot " + String(slotNumber));
}

int getMotorPin(int slotNumber) {
  switch (slotNumber) {
    case 1: return SLOT_1_PIN;
    case 2: return SLOT_2_PIN;
    case 3: return SLOT_3_PIN;
    case 4: return SLOT_4_PIN;
    case 5: return SLOT_5_PIN;
    default: return -1;
  }
}

void printHelp() {
  Serial.println("📚 Available Commands:");
  Serial.println("  VEND:1  - Vend item from slot 1");
  Serial.println("  VEND:2  - Vend item from slot 2");
  Serial.println("  VEND:3  - Vend item from slot 3");
  Serial.println("  VEND:4  - Vend item from slot 4");
  Serial.println("  VEND:5  - Vend item from slot 5");
  Serial.println("  STATUS  - Check system status");
  Serial.println("  PING    - Test connection");
  Serial.println("  RESET   - Restart ESP32");
  Serial.println("  HELP    - Show this help message");
  Serial.println("");
  Serial.println("💡 Commands are case-insensitive");
  Serial.println("🔗 Send commands from Flask server or Serial Monitor");
}