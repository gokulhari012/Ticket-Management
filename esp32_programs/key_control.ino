#include <Arduino.h>

// Define button pins (adjust as needed)
#define ENTER_BTN 'e'
#define BACKSPACE_BTN 'b'

// Variables to store input
String dealer_no = "";
String can_count = "";
int token_id = 0;
String cursor = "delear";

// Function Prototypes
void reset_values();
void token_close();

void update_token(int value){
  token_id = value;
}

void display_token(){
    Serial.println("New token");
    token_id = get_next_token_id();
    clear_all_values();
    reset_values();
    token_value_update(token_id);
}
// Function to reset values
void reset_values() {
    dealer_no = "";
    can_count = "";
}

// Function to close the token and process data
void token_close() {
    add_dealer_from_display(token_id, dealer_no.toInt(), can_count.toInt());
}

// Function to handle button press
void handle_button_press(char button) {
    if (button == ENTER_BTN) {
        Serial.println("Enter key pressed");
        if (cursor == "delear") {
            if (dealer_no == "") {
                Serial.println("Enter the dealer number");
            } else {
                cursor = "can";
                cursor_update_water_can();
            }
        } else {
            if (can_count == "") {
                Serial.println("Enter the can count");
            } else {
                token_close();
                cursor = "delear";
                Serial.println("Token closed");
                display_token();
            }
        }
    } else if (button == BACKSPACE_BTN) {
        Serial.println("Backspace key pressed");
        if (cursor == "delear") {
            if (dealer_no.length() > 0) {
                dealer_no.remove(dealer_no.length() - 1);
                delear_value_update(dealer_no.toInt());
            }
        } else {
            if (can_count.length() > 0) {
                can_count.remove(can_count.length() - 1);
                water_can_count_update(can_count.toInt());
            } else {
                cursor = "delear";
                cursor_update_delear();
            }
        }
    } else {
      int bt = button - '0';
        if (bt >= 0 && bt <= 9) {  // Map button to corresponding number
            Serial.print("Number ");
            Serial.print(bt);
            Serial.println(" pressed");
            if (cursor == "delear") {
                if (dealer_no.length() < 3) {
                    dealer_no += String(bt);
                    delear_value_update(dealer_no.toInt());
                }
            } else {
                if (can_count.length() < 3) {
                    can_count += String(bt);
                    water_can_count_update(can_count.toInt());
                }
            }
        }
      }
}

// Function to check button press
void check_buttonss() {
    if (Serial.available() > 0) { // Check if data is available
          char receivedChar = Serial.read(); // Read the character
              handle_button_press(receivedChar);
      }
}

// Setup function
void key_setup() {
    display_token();
}

// Loop function
void key_loop() {
    check_buttonss();
}


