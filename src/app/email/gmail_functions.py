import imaplib
import email
from email.header import decode_header
import os
import time
from dotenv import load_dotenv
from src.app.utils.database import db_functions


load_dotenv()

# Gmail credentials
EMAIL_USER =  os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def extract_full_email_body(msg):
    """
    Extracts the full email body while keeping the entire email chain.
    Works for both HTML and plain-text emails.
    """
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        decoded = payload.decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        return decoded
                except Exception as e:
                    print(f"Failed to decode part with content type {content_type}: {e}")

    else:
        # Handle single-part messages
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                decoded = payload.decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                return decoded
        except Exception as e:
            print(f"Failed to decode single-part message: {e}")

    return "Unable to extract email body"


def check_email():
    # try:
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASSWORD)

        # Select the Inbox
        mail.select("inbox")

        # Search for unread emails (UNSEEN)
        status, messages = mail.search(None, 'UNSEEN')

        # Convert message IDs into a list
        email_ids = messages[0].split()

        for email_id in email_ids:
            # Fetch the email
            status, msg_data = mail.fetch(email_id, "(X-GM-THRID RFC822)")

            thread_id = None

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    thread_id = response_part[0].split()[2]
                    msg_id = response_part[0].split()[0]
                    msg = email.message_from_bytes(response_part[1])
                    
                     
                    # Decode the email subject
                    raw_subject = msg["Subject"]
                    if raw_subject is not None:
                        subject, encoding = decode_header(raw_subject)[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")
                    else:
                        subject = "(No Subject)"

                    sender = msg.get("From", "(Unknown Sender)")
                   
                    email_body = extract_full_email_body(msg)  # Extract full email body

                    db_functions.store_email(sender=sender,
                                             subject=subject,
                                             body=email_body,
                                             provider='gmail',
                                             thread_id=thread_id,
                                             msg_id=msg_id,
                                             status="new")
                    
                    print('email logged')

            # Mark email as read
            mail.store(email_id, '+FLAGS', '\\Seen')

        # Close the connection
        mail.close()
        mail.logout()

    # except Exception as e:
    #     print(f"Error checking email: {e}")

