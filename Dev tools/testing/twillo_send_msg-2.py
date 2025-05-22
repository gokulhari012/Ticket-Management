from twilio.rest import Client

# Replace with your actual credentials
account_sid = 'AC47072dc2d5361ca5cab0e1a4f7efd369gokul'  #remove the gokul postfix
auth_token = '5ee9d4d01b69688e77bc548fcfbf79c1'
twilio_whatsapp_number = 'whatsapp:+15557390616'  # Provided by Twilio
twilio_number = "+12317902355"

client = Client(account_sid, auth_token)

# Replace with the recipient's WhatsApp number (include country code)
to_whatsapp_number = 'whatsapp:+918220339908'
to_number = '+918220339908'

message = client.messages.create(
    body='Hello! This is a test WhatsApp message sent using Twilio and Python.',
    from_=twilio_number,
    to=to_number
)

print("Message sent. SID:", message.sid)
