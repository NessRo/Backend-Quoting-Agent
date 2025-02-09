import imaplib
import email
from email.header import decode_header
import os
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

load_dotenv()

# Gmail credentials
EMAIL_USER =  os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")



def extract_html_body(html_body):
    """
    Extracts the HTML email content and returns clean text with structure preserved.
    """
    soup = BeautifulSoup(html_body, "html.parser")
    return soup.get_text(separator="\n").strip()

def extract_plain_text(body):
    """
    Extracts full plain-text emails while preserving the entire chain.
    """
    return body.strip()

def extract_full_email_body(msg):
    """
    Extracts the full email body while keeping the entire email chain.
    Works for both HTML and plain-text emails.
    """
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Get the HTML part (preferable)
            if content_type == "text/html" and "attachment" not in content_disposition:
                return extract_html_body(part.get_payload(decode=True).decode())

            # Get the plain text part (fallback)
            elif content_type == "text/plain" and "attachment" not in content_disposition:
                return extract_plain_text(part.get_payload(decode=True).decode())

    else:
        # If it's not multipart, handle as a simple text email
        content_type = msg.get_content_type()
        if content_type == "text/html":
            return extract_html_body(msg.get_payload(decode=True).decode())
        else:
            return extract_plain_text(msg.get_payload(decode=True).decode())


def check_email():
    try:
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

                    print(f"📩 New Email from {sender}: {subject}")
                    print({email_body})
                    print(F"ID is: {thread_id}")

            # Mark email as read
            mail.store(email_id, '+FLAGS', '\\Seen')

        # Close the connection
        mail.close()
        mail.logout()

    except Exception as e:
        print(f"Error checking email: {e}")

# Continuous loop with a polling interval
while True:
    check_email()
    print("📬 Checking for new emails...")  
    time.sleep(60)  # Wait for 60 seconds before checking again