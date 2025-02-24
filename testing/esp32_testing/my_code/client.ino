// #include <WiFi.h>
// #include <HTTPClient.h>

#include <ESP8266WiFi.h>  // ESP8266 WiFi library
#include <ESP8266HTTPClient.h>  // HTTP client for ESP8266
#include <WiFiClient.h>

// WiFi Credentials
const char* ssid = "GOKULHARI";  // Replace with your WiFi SSID
const char* password = "gokulhari012026";  // Replace with your WiFi Password

// Flask Server URL (Change to your computer's IP)
const char* serverUrl = "http://192.168.0.53:5000/add_dealer"; // Replace with your Flask server's IP

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    // Wait for WiFi connection
    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi!");
}

void loop() {
    if (Serial.available()) {
        // Read input from Serial
        String dealer_id = Serial.readStringUntil(' ');  // Read dealer_id
        String water_can_count = Serial.readStringUntil(' ');  // Read water_can_count
        String token_no = Serial.readStringUntil('\n');  // Read token_no

        dealer_id.trim();
        water_can_count.trim();
        token_no.trim();

        if (dealer_id.length() > 0 && water_can_count.length() > 0 && token_no.length() > 0) {
            Serial.println("Sending data to server...");

            if (WiFi.status() == WL_CONNECTED) {
                HTTPClient http;
                
                // Format data as an HTTP form-urlencoded string
                String postData = "dealer_id=" + dealer_id + "&water_can_count=" + water_can_count + "&token_no=" + token_no;

                http.begin(serverUrl);
                http.addHeader("Content-Type", "application/x-www-form-urlencoded");

                // Send POST request
                int httpResponseCode = http.POST(postData);
                
                if (httpResponseCode > 0) {
                    String response = http.getString();
                    Serial.println("Server Response: " + response);
                } else {
                    Serial.print("Error sending POST: ");
                    Serial.println(httpResponseCode);
                }

                http.end();
            } else {
                Serial.println("WiFi Disconnected! Check your connection.");
            }
        }
    }

    delay(1000); // Short delay before checking for new Serial input
}

