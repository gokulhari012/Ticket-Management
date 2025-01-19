import time
import math
from rpi_ws281x import PixelStrip, Color

# Matrix configuration
NUM_LEDS = 135  # 9x15 matrix
DATA_PIN = 18  # Pin connected to WS2812 (GPIO18)
MATRIX_WIDTH = 9
MATRIX_HEIGHT = 15
ROW_1 = 0
ROW_2 = 5
ROW_3 = 10

# Initialize the LED strip
strip = PixelStrip(NUM_LEDS, DATA_PIN)
strip.begin()
strip.setBrightness(128) 

token_value = 0
delear_value = 0
water_can_value = 0

# 5x3 digit patterns (1 = LED on, 0 = LED off)
digits = [
    [ [1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1] ],  # 0
    [ [0, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 0], [1, 1, 1] ],  # 1
    [ [1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1] ],  # 2
    [ [1, 1, 1], [0, 0, 1], [0, 1, 1], [0, 0, 1], [1, 1, 1] ],  # 3
    [ [1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1] ],  # 4
    [ [1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1] ],  # 5
    [ [1, 1, 1], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1] ],  # 6
    [ [1, 1, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1] ],  # 7
    [ [1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1] ],  # 8
    [ [1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1] ]   # 9
]

# Map (x, y) to the zigzag pixel index with flipped orientation
def get_pixel_index(x, y):
    flipped_y = MATRIX_HEIGHT - 1 - y
    if flipped_y % 2 == 0:
        return flipped_y * MATRIX_WIDTH + x
    else:
        return (flipped_y + 1) * MATRIX_WIDTH - x - 1

# Draw a digit on the matrix
def draw_digit(digit, start_x, start_y, color):
    for row in range(5):
        for col in range(3):
            if digits[digit][row][col] == 1:
                pixel_index = get_pixel_index(start_x + col, start_y + row)
                strip.setPixelColor(pixel_index, color)
    
# Display a row of digits using an integer
def display_row(number, start_y, color):
    for i in range(3):
        digit = (number // int(math.pow(10, 2 - i))) % 10
        start_x = i * 3
        draw_digit(digit, start_x, start_y, color)

# Clear the matrix
def clear_matrix():
    for i in range(NUM_LEDS):
        strip.setPixelColor(i, Color(0, 0, 0))

# Main loop
def main():
    strip.setBrightness(128)  # Set brightness (0 to 255): Suggested 128 (50%)
    while True:
        clear_matrix()
        for i in range(1000):
            clear_matrix()  # Display digits in each row
            # displayRow(value, row number, colour)
            display_row(i, ROW_1, Color(255, 0, 0))  # Red
            display_row(999 - i, ROW_2, Color(0, 255, 0))  # Green
            display_row(i, ROW_3, Color(0, 0, 255))  # Blue
            strip.show()
            time.sleep(0.25)

def clear_all_values():
    global token_value, delear_value, water_can_value
    token_value, delear_value, water_can_value = 0, 0, 0


if __name__ == "__main__":
    main()
