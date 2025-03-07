import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
from src.app.utils.database import db_functions
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

# Gmail credentials
EMAIL_USER =  os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_reply(
    from_address,
    to_address,
    original_subject,
    original_message_id,
    reply_body,
    username,
    password
):
    # Prepare the subject: Prepend "Re:" only if it's not already there
    if not original_subject.lower().startswith("re:"):
        subject = "Re: " + original_subject
    else:
        subject = original_subject

    # Create a multipart message
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = subject

    # — The magic for threading —
    msg["In-Reply-To"] = original_message_id
    # If there are multiple references (like a chain), you'd typically join them here.
    # For a simple case, use the same as In-Reply-To. If you have an existing References header from the original,
    # you can append the new message ID. But for now:
    msg["References"] = original_message_id

    # Attach the reply text
    msg.attach(MIMEText(reply_body, "plain"))

    # Use Gmail’s SMTP server with STARTTLS on port 587
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(username, password)
        server.sendmail(from_address, to_address, msg.as_string())

def strip_email_chain(email_text):
    """
    Returns only the most recent message (top part),
    stripping out everything below any recognized reply marker.
    """
    # Some common markers you might see:
    # We'll allow optional leading '>' or spaces before "On ... wrote:"
    # and do a simple approach for "On XX wrote:", "-----Original Message-----", or "From: XY"
    reply_markers = [
        r"^[>\s]*On .+ wrote:$",
        r"^[>\s]*-----Original Message-----$",
        r"^[>\s]*From: .+"
    ]
    
    # Combine them into a single regex
    pattern = re.compile("(" + "|".join(reply_markers) + ")", re.IGNORECASE)
    
    stripped_lines = []
    for line in email_text.splitlines():
        # Check if (after removing leading > / space) it matches a reply marker
        if pattern.match(line):
            # Found the beginning of older chain, so stop
            break
        stripped_lines.append(line)
    
    return "\n".join(stripped_lines).strip()


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

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    thread_id = response_part[0].split()[2]
                    msg_id = response_part[0].split()[0]
                    msg = email.message_from_bytes(response_part[1])

                    message_id_rfc822 = msg.get("Message-ID")      # e.g. <[email protected]>
                    in_reply_to_rfc822 = msg.get("In-Reply-To")    # e.g. <[email protected]>
                    references_rfc822 = msg.get("References") 
                    
                     
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

                    email_body = strip_email_chain(email_body)

                    db_functions.store_email(sender=sender,
                                             subject=subject,
                                             body=email_body,
                                             provider='gmail',
                                             thread_id=thread_id,
                                             msg_id=msg_id,
                                             status="new",
                                             message_id_rfc822=message_id_rfc822,
                                             in_reply_to_rfc822=in_reply_to_rfc822,
                                             references_rfc822=references_rfc822)
                    
                    
                    
                    print('email logged')
    

            # Mark email as read
            mail.store(email_id, '+FLAGS', '\\Seen')

        # Close the connection
        mail.close()
        mail.logout()

    # except Exception as e:
    #     print(f"Error checking email: {e}")