#include <ESP8266WiFi.h>  // ESP8266 WiFi library
#include <ESP8266HTTPClient.h>  // HTTP client for ESP8266
#include <WiFiClient.h>
#include <ESPAsyncWebServer.h>

// WiFi Credentials
const char* ssid = "GOKULHARI";  // Replace with your WiFi SSID
const char* password = "gokulhari012026";  // Replace with your WiFi Password

// Flask Server URL (Change to your computer's IP)
String serverIp = "192.168.0.53:80";
String serverUrlAddDealer = "http://"+serverIp+"/add_dealer_esp32"; // Replace with your Flask server's IP
String serverUrlGetToken = "http://"+serverIp+"/get_tokenId_esp32"; // Replace with your Flask server's IP

String serverUrlUpdateToken = "/esp_update_token";

AsyncWebServer server(80);

// Set your static IP address
IPAddress local_IP(192, 168, 0, 100);  // Change this to your preferred IP
IPAddress gateway(192, 168, 0, 1);      // Your router's IP
IPAddress subnet(255, 255, 255, 0);     // Subnet mask
// IPAddress primaryDNS(8, 8, 8, 8);       // Optional: Google DNS
// IPAddress secondaryDNS(8, 8, 4, 4);     // Optional: Google DNS

void setup() {
    Serial.begin(115200);

        // Connect to Wi-Fi with static IP
    if (!WiFi.config(local_IP, gateway, subnet)) {
        Serial.println("Failed to configure Static IP!");
    }

    WiFi.begin(ssid, password);

    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi!");
    Serial.print("ESP32 Static IP Address: ");
    Serial.println(WiFi.localIP());

    setup_http();
    led_setup();
    key_setup();

}

void setup_http(){
  server.on("/esp_update_token", HTTP_GET, [](AsyncWebServerRequest *request){
          if (request->hasParam("message")) {
              String msg = request->getParam("message")->value();
              Serial.print("Received via Wi-Fi: ");
              Serial.println(msg);
              request->send(200, "text/plain", "Token Received");
              edit_token(msg.toInt());
          } else {
              request->send(400, "text/plain", "Missing parameter");
          }
      });
    server.begin();

}

void edit_token(int token){
  update_token(token);
  token_value_update(token);
}

int get_next_token_id(){
  Serial.println("Getting Token id data from server...");
  int tokenId = 0;
  if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;
      
      // Format data for HTTP POST
      String postData = "";

      http.begin(client, serverUrlGetToken);
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");

      int httpResponseCode = http.POST(postData);
      
    if (httpResponseCode > 0) {
          String response = http.getString();
          Serial.println("Server Response Token ID: " + response);
          tokenId = response.toInt();
      } else {
          Serial.print("Error sending POST for TokenId: ");
          Serial.println(httpResponseCode);
      }

      http.end();
  } else {
      Serial.println("WiFi Disconnected!");
  }
  return tokenId;
}

void add_dealer_from_display(int token_no, int dealer_id, int water_can_count){
  Serial.println("Sending dealer details to server...");

  if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;
      
      // Format data for HTTP POST
      String postData = "dealer_id=" + String(dealer_id) + "&water_can_count=" + String(water_can_count) + "&token_no=" + String(token_no);

      http.begin(client, serverUrlAddDealer);
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");

      int httpResponseCode = http.POST(postData);
      
    if (httpResponseCode > 0) {
          String response = http.getString();
          Serial.println("Server Response Delear update: " + response);
      } else {
          Serial.print("Error sending POST: ");
          Serial.println(httpResponseCode);
      }

      http.end();
  } else {
      Serial.println("WiFi Disconnected!");
  }
}

void loop() {
  key_loop();
}
