import keyboard
import threading

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
                else:
                    if can_count == "":
                        print("Enter the can count")
                    else:
                        cursor = "delear"

            elif key_name == "backspace":
                print("Backspace key released")
                if cursor=="delear":
                    if len(delear_no) > 0:
                        delear_no = delear_no[:-1]
                else:
                    if len(can_count) > 0:
                        can_count = can_count[:-1]
                    else:
                        cursor = "delear"
            else:
                if key_name.isdigit():
                    print(f"Number {key_name} released")
                    if cursor=="delear":
                        if len(delear_no) < 3:
                            delear_no += int(key_name)
                    else:
                        if len(can_count) < 3:
                            can_count += int(key_name)
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


def main_loop():
    read_keyboard()

def start_display_functions():
    t = threading.Thread(target=main_loop)
    t.start()

start_display_functions()
# read_keyboard()
