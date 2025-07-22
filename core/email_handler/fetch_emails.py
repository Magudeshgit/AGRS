import imaplib
import email
from email.header import decode_header
from core.models import EmailComplaint, Complaint
from core.utils.department_contacts import classify_rule_based

from django.utils.timezone import now
from django.contrib.auth.models import User

def fetch_and_process_emails():
    username = ' '
    password = ' '

    # connect to server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    # search for unseen mails
    status, messages = mail.search(None, 'UNSEEN')
    mail_ids = messages[0].split()

    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        from_email = msg.get("From")

        # Get email body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        # Save as EmailComplaint
        email_obj = EmailComplaint.objects.create(
            sender=from_email,
            subject=subject,
            body=body,
            received_at=now()
        )

        # Use rule-based/AI classifier
        department = classify_rule_based(subject, body)

        # Save as actual complaint (assuming user is anonymous/email based)
        default_user = User.objects.filter(username="email_user").first()

        complaint = Complaint.objects.create(
            user=default_user,
            title=subject,
            description=body,
            category="Email",
            department=department,
            contact_email=from_email,
            status="pending"
        )

        email_obj.complaint_linked = complaint
        email_obj.save()

    mail.logout()
