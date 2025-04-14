from twilio.rest import Client
import schedule
import time

# Twilio credentials from your account
account_sid = ''
auth_token = 'ad4cafeece8bda330c87f1a0921b94c0'

client = Client(account_sid, auth_token)

# WhatsApp numbers: 'from_' is your Twilio Sandbox number
def send_whatsapp_message():
    message = client.messages.create(
        from_='whatsapp:+14155238886',  # Twilio sandbox number
        body='Hi, bro Hello from Python via Twilio! ✅',
        to='whatsapp:+918072360277'  # Replace with your number
    )
    print(f"Message sent! SID: {message.sid}")

# 🕒 Schedule the message
schedule_time = "23:33"  # 24-hour format (HH:MM)
schedule.every().day.at(schedule_time).do(send_whatsapp_message)

print(f"Scheduled message at {schedule_time}. Waiting...")

send_whatsapp_message()
# Keep running
while True:
    schedule.run_pending()
    time.sleep(1)
