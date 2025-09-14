#include <WiFiS3.h>
#include <Servo.h>

// WiFi credentials
const char* ssid = "HackTheNorth";
const char* password = "HTN2025!";

// Server setup
WiFiServer server(8080);

// Servo setup
Servo servos[6];
int servoPins[6] = {2, 3, 4, 5, 6, 7};
const int highPosition = 105;  // Servo position for '1' (raised dot)
const int lowPosition = 90;    // Servo position for '0' (lowered dot)

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("Starting Braille Display System...");
  
  // Initialize servos
  for (int i = 0; i < 6; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(lowPosition);  // Start all servos at low position
    delay(100);
  }
  Serial.println("✅ Servos initialized");
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("✅ WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Start server
  server.begin();
  Serial.println("✅ HTTP server started on port 8080");
  Serial.println("Ready to receive Braille patterns!");
}

void setBraillePattern(String pattern) {
  Serial.println("==========================================");
  Serial.println("📍 RECEIVED BRAILLE PATTERN:");
  Serial.print("   Pattern: ");
  Serial.println(pattern);
  
  if (pattern.length() != 6) {
    Serial.println("❌ ERROR: Pattern must be exactly 6 bits");
    return;
  }
  
  // Validate pattern (only 0s and 1s allowed)
  for (int i = 0; i < 6; i++) {
    if (pattern[i] != '0' && pattern[i] != '1') {
      Serial.println("❌ ERROR: Pattern must contain only 0s and 1s");
      return;
    }
  }
  
  Serial.println("📊 SERVO CONTROL:");
  
  // Set each servo based on bit value
  for (int i = 0; i < 6; i++) {
    int position;
    if (pattern[i] == '1') {
      position = highPosition;  // Raised dot
      if (i >= 3) {
        position = 180 - position;
      }
      Serial.print("   Servo ");
      Serial.print(i);
      Serial.print(" (Pin ");
      Serial.print(servoPins[i]);
      Serial.print("): HIGH (");
      Serial.print(position);
      Serial.println("°)");
    } else {
      position = lowPosition;   //  Lowered dot
      Serial.print("   Servo ");
      Serial.print(i);
      Serial.print(" (Pin ");
      Serial.print(servoPins[i]);
      Serial.print("): LOW (");
      Serial.print(position);
      Serial.println("°)");
    }
    
    servos[i].write(position);
    // delay(50);  // Small delay between servo movements
  }
  delay(1000);
  
  Serial.println("✅ Pattern applied successfully!");
  Serial.println("==========================================");

}

void loop() {
  WiFiClient client = server.available();
  
  if (client) {
    Serial.println("🔗 New client connected");
    String request = "";
    
    // Read the HTTP request
    while (client.connected() && client.available()) {
      String line = client.readStringUntil('\n');
      line.trim();
      
      if (line.length() == 0) {
        break;  // End of HTTP headers
      }
      
      if (line.startsWith("GET /braille/")) {
        // Extract pattern from URL: GET /braille/101100
        int startIndex = line.indexOf("/braille/") + 9;
        int endIndex = line.indexOf(" ", startIndex);
        String pattern = line.substring(startIndex, endIndex);
        
        Serial.println("📨 HTTP REQUEST RECEIVED:");
        Serial.print("   Full request: ");
        Serial.println(line);
        Serial.print("   Extracted pattern: ");
        Serial.println(pattern);
        
        setBraillePattern(pattern);
        
        // Send HTTP response
        client.println("HTTP/1.1 200 OK");
        client.println("Content-Type: text/plain");
        client.println("Connection: close");
        client.println();
        client.println("OK: Pattern " + pattern + " applied");
        break;
      }
    }
    
    // Close connection
    client.stop();
    Serial.println("🔌 Client disconnected");
    
    // Reset all servos to low position (90 degrees)
    Serial.println("🔄 Resetting all servos to default LOW position (90°)...");
    for (int i = 0; i < 6; i++) {
      servos[i].write(90);  // Reset to 90 degrees (lowPosition)
      Serial.print("   Servo ");
      Serial.print(i);
      Serial.print(" (Pin ");
      Serial.print(servoPins[i]);
      Serial.println("): 90°");
      // delay(50);
    }
    Serial.println("✅ All servos reset to default position (90°)\n");
  }
}