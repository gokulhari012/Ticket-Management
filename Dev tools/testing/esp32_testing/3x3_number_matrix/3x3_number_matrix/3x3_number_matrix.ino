#include <FastLED.h>

// Matrix configuration
#define NUM_LEDS 135  // 9x15 matrix
#define DATA_PIN 13   // Pin connected to WS2812
#define MATRIX_WIDTH 9
#define MATRIX_HEIGHT 15
#define ROW_1 0
#define ROW_2 5
#define ROW_3 10

CRGB leds[NUM_LEDS];

// 5x3 digit patterns (1 = LED on, 0 = LED off)
const byte digits[10][5][3] = {
  { { 1, 1, 1 }, { 1, 0, 1 }, { 1, 0, 1 }, { 1, 0, 1 }, { 1, 1, 1 } },  // 0
  { { 0, 1, 0 }, { 1, 1, 0 }, { 0, 1, 0 }, { 0, 1, 0 }, { 1, 1, 1 } },  // 1
  { { 1, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 }, { 1, 0, 0 }, { 1, 1, 1 } },  // 2
  { { 1, 1, 1 }, { 0, 0, 1 }, { 0, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 } },  // 3
  { { 1, 0, 1 }, { 1, 0, 1 }, { 1, 1, 1 }, { 0, 0, 1 }, { 0, 0, 1 } },  // 4
  { { 1, 1, 1 }, { 1, 0, 0 }, { 1, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 } },  // 5
  { { 1, 1, 1 }, { 1, 0, 0 }, { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 } },  // 6
  { { 1, 1, 1 }, { 0, 0, 1 }, { 0, 0, 1 }, { 0, 0, 1 }, { 0, 0, 1 } },  // 7
  { { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 } },  // 8
  { { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 } }   // 9
};


// Map (x, y) to the zigzag pixel index with flipped orientation
int getPixelIndex(int x, int y) {
  // Flip the rows to account for the upside-down matrix
  int flippedY = MATRIX_HEIGHT - 1 - y;

  if (flippedY % 2 == 0) {
    // Even row (left to right)
    return flippedY * MATRIX_WIDTH + x;
  } else {
    // Odd row (right to left)
    return (flippedY + 1) * MATRIX_WIDTH - x - 1;
  }
}


// Draw a digit on the matrix
void drawDigit(int digit, int startX, int startY, CRGB color) {
  for (int row = 0; row < 5; row++) {
    for (int col = 0; col < 3; col++) {
      if (digits[digit][row][col] == 1) {
        int pixelIndex = getPixelIndex(startX + col, startY + row);
        leds[pixelIndex] = color;
      }
    }
  }
}

// Display a row of digits using an integer
void displayRow(int number, int startY, CRGB color) {
  for (int i = 0; i < 3; i++) {
    int digit = (number / (int)pow(10, 2 - i)) % 10;  
    int startX = i * 3;                              
    drawDigit(digit, startX, startY, color);
  }
}

// Clear the matrix
void clearMatrix() {
  fill_solid(leds, NUM_LEDS, CRGB::Black);
}

void setup() {
  FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.setBrightness(128);  // Set brightness (0 to 255): SUGGESTED BRIGHTNESS 128 (50%)
}

void loop() {
  clearMatrix();
  for (int i = 0; i < 1000; i++) {
    clearMatrix();  // Display digits in each row
    // displayRow(value, row number, colour);
    displayRow(i, ROW_1, CRGB::Red);
    displayRow(999 - i, ROW_2, CRGB::Green);
    displayRow(i, ROW_3, CRGB::Blue);
    FastLED.show();
    delay(250);
  }
}
