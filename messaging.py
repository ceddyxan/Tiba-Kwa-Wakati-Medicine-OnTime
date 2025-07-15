# messaging.py
import os
from twilio.rest import Client

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = None
if TWILIO_SID and TWILIO_TOKEN:
    client = Client(TWILIO_SID, TWILIO_TOKEN)

def send_sms(phone, message):
    if client and TWILIO_PHONE:
        try:
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE,
                to=phone
            )
        except Exception as e:
            print(f"[TWILIO SMS ERROR] {e}")
    else:
        print(f"[MOCK SMS] To: {phone} | Message: {message}")

def send_whatsapp(phone, message):
    if client and TWILIO_WHATSAPP:
        try:
            client.messages.create(
                body=message,
                from_='whatsapp:' + TWILIO_WHATSAPP,
                to='whatsapp:' + phone
            )
        except Exception as e:
            print(f"[TWILIO WhatsApp ERROR] {e}")
    else:
        print(f"[MOCK WhatsApp] To: {phone} | Message: {message}")

def send_voice(phone, message):
    if client and TWILIO_PHONE:
        try:
            client.calls.create(
                twiml=f'<Response><Say>{message}</Say></Response>',
                from_=TWILIO_PHONE,
                to=phone
            )
        except Exception as e:
            print(f"[TWILIO Voice ERROR] {e}")
    else:
        print(f"[MOCK Voice] To: {phone} | Message: {message}") 