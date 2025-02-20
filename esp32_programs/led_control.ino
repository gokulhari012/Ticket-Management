#include <Adafruit_NeoPixel.h>

#define NUM_LEDS 135   // 9x15 matrix
#define DATA_PIN 2    // Pin connected to WS2812
#define MATRIX_WIDTH 9
#define MATRIX_HEIGHT 15
#define BRIGHTNESS 128

Adafruit_NeoPixel strip(NUM_LEDS, DATA_PIN, NEO_GRB + NEO_KHZ800);

int token_value = 0;
int dealer_value = 0;
int water_can_value = 0;

#define ROW_1 0
#define ROW_2 5
#define ROW_3 10

// 5x3 digit patterns (1 = LED on, 0 = LED off)
const int digits[10][5][3] = {
    {{1, 1, 1}, {1, 0, 1}, {1, 0, 1}, {1, 0, 1}, {1, 1, 1}},  // 0
    {{0, 1, 0}, {1, 1, 0}, {0, 1, 0}, {0, 1, 0}, {1, 1, 1}},  // 1
    {{1, 1, 1}, {0, 0, 1}, {1, 1, 1}, {1, 0, 0}, {1, 1, 1}},  // 2
    {{1, 1, 1}, {0, 0, 1}, {0, 1, 1}, {0, 0, 1}, {1, 1, 1}},  // 3
    {{1, 0, 1}, {1, 0, 1}, {1, 1, 1}, {0, 0, 1}, {0, 0, 1}},  // 4
    {{1, 1, 1}, {1, 0, 0}, {1, 1, 1}, {0, 0, 1}, {1, 1, 1}},  // 5
    {{1, 1, 1}, {1, 0, 0}, {1, 1, 1}, {1, 0, 1}, {1, 1, 1}},  // 6
    {{1, 1, 1}, {0, 0, 1}, {0, 0, 1}, {0, 0, 1}, {0, 0, 1}},  // 7
    {{1, 1, 1}, {1, 0, 1}, {1, 1, 1}, {1, 0, 1}, {1, 1, 1}},  // 8
    {{1, 1, 1}, {1, 0, 1}, {1, 1, 1}, {0, 0, 1}, {1, 1, 1}}   // 9
};

// Map (x, y) to pixel index in zigzag pattern
int get_pixel_index(int x, int y) {
    int flipped_y = MATRIX_HEIGHT - 1 - y;
    return (flipped_y % 2 == 0) ? (flipped_y * MATRIX_WIDTH + x)
                                : ((flipped_y + 1) * MATRIX_WIDTH - x - 1);
}

// Draw a digit on the matrix
void draw_digit(int digit, int start_x, int start_y, uint32_t color) {
    for (int row = 0; row < 5; row++) {
        for (int col = 0; col < 3; col++) {
            if (digits[digit][row][col] == 1) {
                int pixel_index = get_pixel_index(start_x + col, start_y + row);
                strip.setPixelColor(pixel_index, color);
            }
        }
    }
}

// Display a row of digits
void display_row(int number, int start_y, uint32_t color) {
    for (int i = 0; i < 3; i++) {
        int digit = (number / (int)pow(10, 2 - i)) % 10;
        int start_x = i * 3;
        draw_digit(digit, start_x, start_y, color);
    }
}


// Clear matrix
void clear_matrix() {
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 0));
    }
}

void clear_all_values(){
  token_value = 0;
  dealer_value = 0;
  water_can_value = 0;
}

void token_value_update(int value){
    token_value = value;
    if (cursor == "delear"){
      cursor_update_delear();
    }
    else{
      cursor_update_water_can();
    }
}

void delear_value_update(int value){
    dealer_value = value;
    cursor_update_delear();
}

void water_can_count_update(int value){
    water_can_value = value;
    cursor_update_water_can();
}

void cursor_update_delear(){
    clear_matrix();
    display_row(token_value, ROW_1, strip.Color(0, 0, 255));  // Blue
    display_row(dealer_value, ROW_2, strip.Color(255, 0, 0)); // Red
    display_row(water_can_value, ROW_3, strip.Color(0, 255, 0)); // Green
    strip.show();
    delay(250);
}

void cursor_update_water_can(){
    clear_matrix();
    display_row(token_value, ROW_1, strip.Color(0, 0, 255));  // Blue
    display_row(dealer_value, ROW_2, strip.Color(0, 255, 0)); // Green
    display_row(water_can_value, ROW_3, strip.Color(255, 0, 0)); // Red
    strip.show();
    delay(250);
}

void led_setup() {
    //delay(500);  // Small delay before initializing NeoPixel
    strip.begin();
    strip.setBrightness(BRIGHTNESS);
    strip.show(); // Initialize all pixels to off
    Serial.println("led setup completed");
}



