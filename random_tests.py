import smtplib
import ssl
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    message_id = f"<{uuid.uuid4()}@gmail.com>"

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

    msg["Message-ID"] = message_id

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

# ---------------------------------------
# Example usage (putting it all together)
# ---------------------------------------
if __name__ == "__main__":
    # 1. First, get the original subject & message id from your last email
    # 2. Compose your reply
    body = "This is my reply.\n\nThanks!"
    
    # 3. Send it
    send_reply(
        from_address="bazaris.quoting.agent@gmail.com",
        to_address="nrostane@gmail.com",
        original_subject='Re: Test',
        original_message_id='<B59CFB14-6498-4F4D-A165-84F1070F6178@gmail.com>',
        reply_body=body,
        username="bazaris.quoting.agent@gmail.com",
        password="bofe zipx owpn iwrq"
    )
    print("Reply sent!")