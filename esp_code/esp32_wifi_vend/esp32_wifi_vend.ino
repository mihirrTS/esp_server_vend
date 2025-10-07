/*
 * ESP32 WiFi Vending Machine
 * 
 * This version connects to WiFi and communicates with Flask server via HTTP
 * Replace the mock version with actual network communication
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>

// ================================
// CONFIGURATION - UPDATE THESE!
// ================================
const char* WIFI_SSID = "Mihirr";          // Replace with your WiFi name
const char* WIFI_PASSWORD = "12345678";   // Replace with your WiFi password
const int FLASK_SERVER_PORT = 5000;                // Flask server port (usually 5000)

// Auto-detected variables (no need to configure)
String FLASK_SERVER_IP = "";                       // Auto-detected during setup
String deviceId = "";                              // Auto-generated device ID

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
  Serial.println("ESP32 WiFi Vending Machine v2.1");
  Serial.println("========================================");
  
  // Connect to WiFi
  connectToWiFi();
  
  // Auto-discover Flask server
  discoverFlaskServer();
  
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
  
  // Poll server for commands (optimized for faster response)
  static unsigned long lastPoll = 0;
  if (millis() - lastPoll > 2000) {  // Poll every 2 seconds instead of 5
    checkForCommands();
    lastPoll = millis();
  }
  
  // Heartbeat indicator (faster blink)
  if (millis() - lastHeartbeat > 1000) {  // Blink every 1 second
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);  // Longer blink for better visibility
    digitalWrite(STATUS_LED_PIN, LOW);
    lastHeartbeat = millis();
  }
  
  delay(100);
}

void discoverFlaskServer() {
  Serial.println("🔍 Fast Flask server discovery...");
  
  // Generate unique device ID
  deviceId = "ESP32_" + WiFi.macAddress();
  deviceId.replace(":", "");
  
  // Get network info
  IPAddress localIP = WiFi.localIP();
  IPAddress gateway = WiFi.gatewayIP();
  String networkBase = String(localIP[0]) + "." + String(localIP[1]) + "." + String(localIP[2]) + ".";
  
  Serial.println("📡 Smart scanning: " + networkBase + "x");
  
  // Strategy 1: Try gateway first (common for development)
  Serial.println("🎯 Testing gateway: " + gateway.toString());
  if (testFlaskServerFast(gateway.toString())) {
    FLASK_SERVER_IP = gateway.toString();
    Serial.println("✅ Flask server found at gateway: " + FLASK_SERVER_IP);
    return;
  }
  
  // Strategy 2: Try broadcast discovery (fastest method)
  if (discoverViaBroadcast()) {
    Serial.println("✅ Flask server found via broadcast: " + FLASK_SERVER_IP);
    return;
  }
  
  // Strategy 3: Smart range scanning (only most likely IPs)
  String likelyIPs[] = {
    networkBase + "1",     // Gateway
    networkBase + "100",   // Common static
    networkBase + "10",    // Common static  
    networkBase + "2",     // Common DHCP start
    networkBase + "20",    // Common dev range
    networkBase + String(localIP[3] - 1),  // IP before this one
    networkBase + String(localIP[3] + 1)   // IP after this one
  };
  
  Serial.println("⚡ Quick scan of likely IPs...");
  for (int i = 0; i < 7; i++) {
    if (likelyIPs[i] == localIP.toString()) continue;
    Serial.print(".");
    if (testFlaskServerFast(likelyIPs[i])) {
      FLASK_SERVER_IP = likelyIPs[i];
      Serial.println("\n✅ Flask server found: " + FLASK_SERVER_IP);
      return;
    }
  }
  
  Serial.println("\n❌ Flask server not found");
  Serial.println("💡 Ensure Flask server is running on port " + String(FLASK_SERVER_PORT));
  Serial.println("💡 Or manually set FLASK_SERVER_IP in code");
}

bool discoverViaBroadcast() {
  // Try mDNS-style discovery first
  Serial.println("📻 Trying broadcast discovery...");
  
  // Create UDP socket for broadcast
  WiFiUDP udp;
  if (udp.begin(12345)) {
    // Send broadcast packet
    udp.beginPacket("255.255.255.255", 12346);
    udp.print("ESP32_DISCOVERY_REQUEST");
    udp.endPacket();
    
    // Wait for response (very short timeout)
    unsigned long start = millis();
    while (millis() - start < 500) {  // 500ms timeout
      int packetSize = udp.parsePacket();
      if (packetSize) {
        String response = udp.readString();
        if (response.startsWith("FLASK_SERVER:")) {
          String serverIP = response.substring(13);
          serverIP.trim();
          if (testFlaskServerFast(serverIP)) {
            FLASK_SERVER_IP = serverIP;
            udp.stop();
            return true;
          }
        }
      }
      delay(10);
    }
    udp.stop();
  }
  return false;
}

bool testFlaskServerFast(String ip) {
  HTTPClient testHttp;
  testHttp.begin("http://" + ip + ":" + String(FLASK_SERVER_PORT) + "/status");
  testHttp.setTimeout(800);  // Very fast timeout - 800ms
  testHttp.setConnectTimeout(500);  // Fast connection timeout
  
  int httpCode = testHttp.GET();
  String response = "";
  
  if (httpCode > 0) {
    response = testHttp.getString();
  }
  
  testHttp.end();
  
  // Check for Flask server signature
  if (httpCode == 200 && (response.indexOf("vending") >= 0 || response.indexOf("flask") >= 0 || response.indexOf("status") >= 0)) {
    return true;
  }
  
  return false;
}

void connectToWiFi() {
  Serial.print("🔗 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  // WiFi optimization settings for faster response
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);
  WiFi.setSleep(false);  // Disable WiFi sleep for faster response
  
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
    Serial.print("📍 ESP32 IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("🌐 Gateway IP: ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("🔍 Will scan for Flask server on port ");
    Serial.println(FLASK_SERVER_PORT);
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
    Serial.println("Please check SSID/password and try again");
  }
}

void registerWithServer() {
  if (WiFi.status() != WL_CONNECTED || FLASK_SERVER_IP == "") return;
  
  Serial.println("📡 Registering with Flask server at: " + FLASK_SERVER_IP);
  
  http.begin("http://" + FLASK_SERVER_IP + ":" + String(FLASK_SERVER_PORT) + "/esp32/register");
  http.addHeader("Content-Type", "application/json");
  
  // Send ESP32 info to server
  StaticJsonDocument<200> doc;
  doc["device_id"] = deviceId;
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
  if (WiFi.status() != WL_CONNECTED || !systemReady || FLASK_SERVER_IP == "") return;
  
  String url = "http://" + FLASK_SERVER_IP + ":" + String(FLASK_SERVER_PORT) + "/esp32/commands/" + deviceId;
  http.begin(url);
  
  // Optimize HTTP settings for faster response
  http.setTimeout(3000);        // 3 second timeout instead of default 5
  http.setConnectTimeout(2000); // 2 second connection timeout
  
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