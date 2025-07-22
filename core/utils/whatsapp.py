from twilio.rest import Client
from core.utils.phone import format_phone_number
from django.conf import settings
from core.models import WhatsAppLog

account_sid = settings.TWILIO_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

FROM_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Twilio Sandbox number

def send_whatsapp_message(to_number, message_text, related_complaint=None, recipient_role='user'):
    try:
        formatted_number = format_phone_number(to_number)
        full_to = f'whatsapp:{formatted_number}'

        message = client.messages.create(
            body=message_text,
            from_=FROM_WHATSAPP_NUMBER,
            to=full_to
        )

        WhatsAppLog.objects.create(
            to_number=formatted_number,
            message_text=message_text,
            status='sent',
            complaint=related_complaint,
            recipient_role=recipient_role
        )

        return True
    except Exception as e:
        WhatsAppLog.objects.create(
            to_number=to_number,
            message_text=message_text,
            status='failed',
            complaint=related_complaint,
            recipient_role=recipient_role,
            error=str(e)
        )
        return False
