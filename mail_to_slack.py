import imaplib
import email
import requests
import os
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)

# Configuration
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

IMAP_SERVER = "mail.infomaniak.com"
IMAP_PORT = 993

# Validate Environment Variables
if not EMAIL or not PASSWORD or not SLACK_WEBHOOK:
    logging.error("Missing environment variables: EMAIL, PASSWORD, or SLACK_WEBHOOK.")
    exit(1)


# Function to send message to Slack
def send_to_slack(subject, sender, date, body):
    slack_message = {
        "text": f"*New Email Received*:\n"
        f"*From:* {sender}\n"
        f"*Subject:* {subject}\n"
        f"*Date:* {date}\n"
        f"*Body:* {body}..."
    }
    response = requests.post(SLACK_WEBHOOK, json=slack_message)
    if response.status_code != 200:
        logging.error(
            f"Failed to send message to Slack: {response.status_code}, {response.text}"
        )


# Connect to Mail Server
try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
except Exception as e:
    logging.error(f"Failed to connect or login to mail server: {e}")
    exit(1)

# Search for unseen emails
try:
    status, messages = mail.search(None, "(UNSEEN)")
    messages = messages[0].split()

    if not messages:
        logging.info("No unseen emails.")
        mail.logout()
        exit(0)

    # Process each email and forward to Slack
    for mail_id in messages:
        status, msg_data = mail.fetch(mail_id, "(BODY.PEEK[])")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                email_message = email.message_from_bytes(response_part[1])
                sender = email_message["From"]
                subject = email_message["Subject"]
                date = email_message["Date"]

                # Extract email body
                body = ""
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain" and not part.get(
                        "Content-Disposition"
                    ):
                        try:
                            body = part.get_payload(decode=True).decode(
                                part.get_content_charset() or "utf-8"
                            )
                        except Exception as e:
                            logging.error(f"Failed to decode email body: {e}")
                            body = "Unable to decode the email body."

                # Truncate long body
                body_preview = body[:1000]

                # Send to Slack
                send_to_slack(subject, sender, date, body_preview)

except Exception as e:
    logging.error(f"Error processing emails: {e}")

finally:
    mail.logout()
