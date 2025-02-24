#define DEBUG_ALL
#define FORCE_TEMPLATED_NOPS
#include <ESP32-USB-Soft-Host.h>
#include "driver/timer.h"
#include <key_to_char.h>
//#include <Wire.h> 
//#include <LiquidCrystal_I2C.h>
#define PROFILE_NAME "Default Wroom"
// DP-->Green
// DM-->White
#define DP_P0  18  // always enabled
#define DM_P0  19  // always enabled
#define DP_P1  -1  // Disable extra ports if not needed
#define DM_P1  -1
#define DP_P2  -1
#define DM_P2  -1
#define DP_P3  -1
#define DM_P3  -1

//LiquidCrystal_I2C lcd(0x27,16,2);


String text="";


void parseKeyboardReport(uint8_t *report) {
  uint8_t modifierKeys = report[0]; // Modifier keys (Shift, Ctrl, Alt)
  uint8_t keyCode = report[2];      // The key code (this can be extended to handle more keys)

  //Serial.print("Modifier Keys: ");
  //Serial.print(keyModifierToString(modifierKeys));
  //Serial.println();

  //Serial.print("Key Pressed: ");
  if (keyCode == 0) {
    //Serial.println("No key pressed");
  } else {
    const char* key = keycodeToChar(keyCode); // Convert the key code to a char (you can expand this)
    if(key=="Backspace")
    {
      if(text!="")
      {text.remove(text.length()-1);}
    }
    else{
    text.concat(key);}
    //lcd.setCursor(0,0);
    //lcd.print(text+" ");
    Serial.println(key);
    Serial.println(text);
  }
}

// Helper function to convert keycode to character
// Function to convert a keycode to a character using the lookup table
const char* keycodeToChar(uint8_t keyCode) {
  if (keyCode < 128) {
    return keyLookupTable[keyCode];  // Lookup the character
  }
  //return "?";  // For unknown key codes
}

// Function to convert modifier keycode to string
const char* keyModifierToString(uint8_t modifierCode) {
  if (modifierCode < 8) {
    return keyModifierLookup[modifierCode];
  }
  return "Unknown Modifier";
}

static void my_USB_DetectCB(uint8_t usbNum, void *dev) {
    sDevDesc *device = (sDevDesc*)dev;
    Serial.printf("New device detected on USB#%d\n", usbNum);
    Serial.printf("Vendor ID: 0x%04x, Product ID: 0x%04x\n", device->idVendor, device->idProduct);
}

static void my_USB_PrintCB(uint8_t usbNum, uint8_t byte_depth, uint8_t* data, uint8_t data_len) {
    //Serial.print("USB Data: ");
   /* for (int k = 0; k < data_len; k++) {
        Serial.printf("0x%02x ", data[k]);
    }*/
    //Serial.print( data[2]);
    parseKeyboardReport(data); 
    Serial.println();
}

usb_pins_config_t USB_Pins_Config = { DP_P0, DM_P0, DP_P1, DM_P1, DP_P2, DM_P2, DP_P3, DM_P3 };

void setup() {
    Serial.begin(115200);
    //lcd.init();                      // initialize the lcd 
   
    //lcd.backlight();
    Serial.println("Initializing USB Soft Host...");
    
    USH.setOnConfigDescCB(Default_USB_ConfigDescCB);
    USH.setOnIfaceDescCb(Default_USB_IfaceDescCb);
    USH.setOnHIDDevDescCb(Default_USB_HIDDevDescCb);
    USH.setOnEPDescCb(Default_USB_EPDescCb);

    if (USH.init(USB_Pins_Config, my_USB_DetectCB, my_USB_PrintCB)) {
        Serial.println("USB Host Initialized Successfully!");
    } else {
        Serial.println("USB Host Initialization Failed!");
    }
}

void loop() {
    delay(1000);  // Keep the loop running
}
