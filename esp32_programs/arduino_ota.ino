#include <ArduinoOTA.h>

void ota_setup(){
   // OTA Setup
    ArduinoOTA.onStart([]() {
        keyboard_pause();
        Serial.println("\nOTA Update Start...");
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("\nOTA Update Complete!");
    });

    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress * 100) / total);
    });

    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("OTA Error [%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

    ArduinoOTA.begin();
    Serial.println("ESP32 OTA Ready!");
}

void ota_loop() {
    ArduinoOTA.handle(); // Check for OTA updates
}