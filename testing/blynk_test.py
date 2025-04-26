import requests
from datetime import datetime
import time

# Your Blynk credentials
BLYNK_AUTH_TOKEN = 'Your_Blynk_Auth_Token_Here'

BLYNK_TEMPLATE_ID = "TMPL30bfSmreb"
BLYNK_TEMPLATE_NAME = "Water Can Management"
BLYNK_AUTH_TOKEN = "UR19Oqzy9tEpBMJkyglVvSxPBBJppNoR"

VIRTUAL_PIN = 'V0'


# Initialize can count
can_count = 0

def send_to_blynk(count):
    url = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH_TOKEN}&{VIRTUAL_PIN}={count}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"[{datetime.now()}] Sent count {count} to Blynk!")
        else:
            print(f"[{datetime.now()}] Failed to send: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def reset_daily_count():
    global can_count
    can_count = 0
    print(f"[{datetime.now()}] Count reset to 0")

# Example: Simulate can counting
def simulate_can_collection():
    global can_count
    while True:
        can_count += 1  # Increment count
        send_to_blynk(can_count)

        # Reset at midnight (00:00)
        current_time = datetime.now()
        if current_time.hour == 0 and current_time.minute == 0:
            reset_daily_count()

        time.sleep(10)  # send every 10 seconds (adjust as needed)

if __name__ == "__main__":
    simulate_can_collection()