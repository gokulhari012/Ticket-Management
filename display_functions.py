import keyboard
from app import get_next_token_id, add_dealer_from_display, app
from led_control import token_value_update, delear_value_update, water_can_count_update, clear_all_values, cursor_update_delear, cursor_update_water_can
import time

is_new_token = True
cursor = "delear"
delear_no = ""
can_count = ""

def display_token():
    global is_new_token
    print("new token")
    if is_new_token:
        token_id = "001"
        with app.app_context():
            token_id = get_next_token_id()
        clear_all_values()
        reset_values()
        token_value_update(token_id)
        is_new_token = False

def reset_values():
    global delear_no, can_count
    delear_no, can_count = "", ""

def token_close():
    global is_new_token
    add_dealer_from_display(delear_no, can_count)
    is_new_token = True

def on_release(key):
    global cursor, delear_no, can_count
    try:
        if key.event_type == keyboard.KEY_UP:
            key_name = key.name 
            if key_name == "enter":
                print("Enter key released")
                if cursor=="delear":
                    if delear_no == "":
                        print("Enter the delear no")
                    else:
                        cursor = "can" 
                        cursor_update_water_can()
                else:
                    if can_count == "":
                        print("Enter the can count")
                    else:
                        with app.app_context():
                            token_close()
                            cursor = "delear"
                            print("token closed")
                            display_token()

            elif key_name == "backspace":
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
                        cursor_update_delear()
            else:
                if key_name.isdigit():
                    print(f"Number {key_name} released")
                    if cursor=="delear":
                        if len(delear_no) < 3:
                            delear_no += key_name
                            delear_value_update(delear_no)
                    else:
                        if len(can_count) < 3:
                            can_count += key_name
                            water_can_count_update(can_count)
    except AttributeError:
        print(f"Special key {key} pressed")
    except Exception as e:
        print(f"Error: {e}")

def read_keyboard():
    print("Listening for keyboard input. Press 'Esc' to exit.")
    # Start listening for key events
    keyboard.hook(on_release)
    # Wait until 'Esc' key is pressed to exit
    keyboard.wait('esc')


def main_program():
    display_token()
    read_keyboard()

def start_display_functions():
    time.sleep(5)
    main_program()

