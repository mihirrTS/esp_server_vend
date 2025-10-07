/*
 * ESP32 WiFi Vending Machine
 * 
 * This version connects to WiFi and communicates with Flask server via HTTP
 * Replace the mock version with actual network communication
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ================================
// CONFIGURATION - UPDATE THESE!
// ================================
const char* WIFI_SSID = "YOUR_WIFI_NAME";          // Replace with your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";   // Replace with your WiFi password
const char* FLASK_SERVER_IP = "192.168.1.100";     // Replace with your computer's IP
const int FLASK_SERVER_PORT = 5000;

// Pin definitions
#define SLOT_1_PIN 2
#define SLOT_2_PIN 4
#define SLOT_3_PIN 5
#define SLOT_4_PIN 18
#define SLOT_5_PIN 19
#define STATUS_LED_PIN 2

// Global variables
WiFiClient wifiClient;
HTTPClient http;
unsigned long lastHeartbeat = 0;
bool systemReady = false;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Initialize pins
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(SLOT_1_PIN, OUTPUT);
  pinMode(SLOT_2_PIN, OUTPUT);
  pinMode(SLOT_3_PIN, OUTPUT);
  pinMode(SLOT_4_PIN, OUTPUT);
  pinMode(SLOT_5_PIN, OUTPUT);
  
  // Set all pins to LOW
  digitalWrite(STATUS_LED_PIN, LOW);
  digitalWrite(SLOT_1_PIN, LOW);
  digitalWrite(SLOT_2_PIN, LOW);
  digitalWrite(SLOT_3_PIN, LOW);
  digitalWrite(SLOT_4_PIN, LOW);
  digitalWrite(SLOT_5_PIN, LOW);
  
  Serial.println("========================================");
  Serial.println("ESP32 WiFi Vending Machine v2.0");
  Serial.println("========================================");
  
  // Connect to WiFi
  connectToWiFi();
  
  // Register with Flask server
  registerWithServer();
  
  Serial.println("✅ System ready for network commands!");
  Serial.println("🌐 Flask server can now send HTTP requests");
  Serial.println("========================================");
  
  systemReady = true;
}

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi disconnected, attempting reconnection...");
    connectToWiFi();
  }
  
  // Poll server for commands (alternative to webhooks)
  static unsigned long lastPoll = 0;
  if (millis() - lastPoll > 5000) {  // Poll every 5 seconds
    checkForCommands();
    lastPoll = millis();
  }
  
  // Heartbeat indicator
  if (millis() - lastHeartbeat > 2000) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(50);
    digitalWrite(STATUS_LED_PIN, LOW);
    lastHeartbeat = millis();
  }
  
  delay(100);
}

void connectToWiFi() {
  Serial.print("🔗 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected!");
    Serial.print("📍 IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("🌐 Flask server: http://");
    Serial.print(FLASK_SERVER_IP);
    Serial.print(":");
    Serial.println(FLASK_SERVER_PORT);
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
    Serial.println("Please check SSID/password and try again");
  }
}

void registerWithServer() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  Serial.println("📡 Registering with Flask server...");
  
  http.begin(String("http://") + FLASK_SERVER_IP + ":" + FLASK_SERVER_PORT + "/esp32/register");
  http.addHeader("Content-Type", "application/json");
  
  // Send ESP32 info to server
  StaticJsonDocument<200> doc;
  doc["device_id"] = WiFi.macAddress();
  doc["ip_address"] = WiFi.localIP().toString();
  doc["status"] = "online";
  doc["slots_available"] = 5;
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
    String response = http.getString();
    Serial.println("✅ Registration successful!");
    Serial.println("Response: " + response);
  } else {
    Serial.println("❌ Registration failed");
    Serial.println("Make sure Flask server is running");
  }
  
  http.end();
}

void checkForCommands() {
  if (WiFi.status() != WL_CONNECTED || !systemReady) return;
  
  String url = String("http://") + FLASK_SERVER_IP + ":" + FLASK_SERVER_PORT + "/esp32/commands/" + WiFi.macAddress();
  http.begin(url);
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String payload = http.getString();
    
    if (payload.length() > 0 && payload != "null") {
      Serial.println("📨 Received command from server: " + payload);
      
      // Parse JSON command
      StaticJsonDocument<200> doc;
      deserializeJson(doc, payload);
      
      String command = doc["command"];
      int slot = doc["slot"];
      
      if (command == "VEND" && slot >= 1 && slot <= 5) {
        vendSlot(slot);
        
        // Send confirmation back to server
        sendConfirmation(slot, true, "Item dispensed successfully");
      }
    }
  }
  
  http.end();
}

void vendSlot(int slotNumber) {
  Serial.println("🎯 Vending slot " + String(slotNumber) + "...");
  
  systemReady = false;
  digitalWrite(STATUS_LED_PIN, HIGH);
  
  // Get motor pin
  int motorPin = getMotorPin(slotNumber);
  
  // Activate motor
  Serial.println("⚡ Activating motor for slot " + String(slotNumber));
  digitalWrite(motorPin, HIGH);
  delay(1000);  // Motor run time
  
  // Simulate sensor check
  Serial.println("👁️ Checking dispense sensor...");
  delay(300);
  
  // 90% success rate simulation
  bool vendSuccess = (random(100) < 90);
  
  if (vendSuccess) {
    Serial.println("✅ Item successfully dispensed from slot " + String(slotNumber));
    
    // Success LED pattern
    for (int i = 0; i < 3; i++) {
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(100);
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(100);
    }
  } else {
    Serial.println("❌ Vending failed - item may be stuck");
  }
  
  // Deactivate motor
  digitalWrite(motorPin, LOW);
  digitalWrite(STATUS_LED_PIN, LOW);
  systemReady = true;
  
  Serial.println("✨ Vending operation completed");
}

void sendConfirmation(int slot, bool success, String message) {
  String url = String("http://") + FLASK_SERVER_IP + ":" + FLASK_SERVER_PORT + "/esp32/confirm";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<300> doc;
  doc["device_id"] = WiFi.macAddress();
  doc["slot"] = slot;
  doc["success"] = success;
  doc["message"] = message;
  doc["timestamp"] = millis();
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
    Serial.println("📤 Confirmation sent to server");
  } else {
    Serial.println("❌ Failed to send confirmation");
  }
  
  http.end();
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

// Optional: Handle commands via Serial for debugging
void serialEvent() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("VEND:")) {
      int slot = command.substring(5).toInt();
      if (slot >= 1 && slot <= 5) {
        vendSlot(slot);
      }
    } else if (command == "STATUS") {
      Serial.println("WiFi: " + String(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected"));
      Serial.println("IP: " + WiFi.localIP().toString());
      Serial.println("Server: " + String(FLASK_SERVER_IP) + ":" + String(FLASK_SERVER_PORT));
    }
  }
}