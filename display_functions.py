from pynput import keyboard
import threading
from app import get_next_token_id, add_dealer_from_display
from led_control import token_value_update, delear_value_update, water_can_count_update, clear_all_values

is_new_token = True
cursor = "delear"
delear_no = ""
can_count = ""

def display_token():
    global is_new_token
    if is_new_token:
        token_id = get_next_token_id()
        clear_all_values()
        token_value_update(token_id)
        is_new_token = False

def token_close():
    global is_new_token
    add_dealer_from_display(delear_no, can_count)
    is_new_token = True

def on_release(key):
    global cursor, delear_no, can_count
    try:
        if key == keyboard.Key.enter:
            print("Enter key released")
            if cursor=="delear":
                if delear_no == "":
                    print("Enter the delear no")
                else:
                    cursor = "can" 
            else:
                if can_count == "":
                    print("Enter the can count")
                else:
                    token_close()
                    cursor = "delear"

        elif key == keyboard.Key.backspace:
            print("Backspace key released")
            if cursor=="delear":
                if len(delear_no) > 0:
                    delear_no = delear_no[:-1]
                    delear_value_update(delear_no)
            else:
                if len(can_count) > 0:
                    can_count = can_count[:-1]
                    water_can_count_update(can_count)
                else:
                    cursor = "delear"
        else:
            key_str = str(key).replace("'", "")  # Remove quotes from the key name
            if key_str.isdigit():
                print(f"Number {key_str} released")
                if cursor=="delear":
                    if len(delear_no) < 3:
                        delear_no += key_str
                        delear_value_update(delear_no)
                else:
                    if len(can_count) < 3:
                        can_count += key_str
                        water_can_count_update(can_count)

    except AttributeError:
        print(f"Special key {key} pressed")
    except Exception as e:
        print(f"Error: {e}")

def read_keyboard():
    with keyboard.Listener(on_release=on_release) as listener:
        print("Listening for keyboard input. Press 'Esc' to exit.")
        listener.join()

def main_loop():
    t = threading.Thread(target=read_keyboard)
    t.start()
    while True:
        display_token()

def start_display_functions():
    t = threading.Thread(target=main_loop)
    t.start()

