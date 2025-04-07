import imaplib
import email
import requests
import os

# Configuration
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

IMAP_SERVER = "mail.infomaniak.com"
IMAP_PORT = 993

# Function to send message to Slack
def send_to_slack(subject, sender, date, body):
    slack_message = {
        "text": f"*New Email Received*:\n"
                f"*From:* {sender}\n"
                f"*Subject:* {subject}\n"
                f"*Date:* {date}\n"
                f"*Body:* {body[:1000]}..."  # Truncate body to 1000 chars
    }
    response = requests.post(SLACK_WEBHOOK, json=slack_message)
    if response.status_code != 200:
        print(f"Failed to send message to Slack: {response.status_code}, {response.text}")

# Connect to the mail server
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(EMAIL, PASSWORD)
mail.select("inbox")

# Search for unseen emails
status, messages = mail.search(None, "(UNSEEN)")
messages = messages[0].split()

if not messages:
    print("No new emails to process")
    mail.logout()
    exit()

# Process each email and forward to Slack
for mail_id in messages:
    status, msg_data = mail.fetch(mail_id, "(BODY.PEEK[])")

    for response_part in msg_data:
        if isinstance(response_part, tuple):
            email_message = email.message_from_bytes(response_part[1])
            sender = email_message["From"]
            subject = email_message["Subject"]
            date = email_message["Date"]

            # Extract email body with charset handling
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset()
                        if charset is None:
                            charset = "utf-8"
                        try:
                            body = part.get_payload(decode=True).decode(charset, errors="replace")
                        except Exception as e:
                            print(f"Error decoding part: {e}")
                        break  # Use the first text/plain part
            else:
                charset = email_message.get_content_charset()
                if charset is None:
                    charset = "utf-8"
                try:
                    body = email_message.get_payload(decode=True).decode(charset, errors="replace")
                except Exception as e:
                    print(f"Error decoding body: {e}")

            # Send to Slack
            send_to_slack(subject, sender, date, body)

# Logout
mail.logout()
