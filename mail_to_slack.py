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
        f"*Body:* {body[:1000]}..."  # Truncate body to 500 chars
    }
    response = requests.post(SLACK_WEBHOOK, json=slack_message)
    if response.status_code != 200:
        print(
            f"Failed to send message to Slack: {response.status_code}, {response.text}"
        )


# Connect to the mail server
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(EMAIL, PASSWORD)
mail.select("inbox")

# Search for unseen emails
status, messages = mail.search(None, "(UNSEEN)")
messages = messages[0].split()


# Process each email and forward to Slack
for mail_id in messages:
    status, msg_data = mail.fetch(mail_id, "(RFC822)")

    for response_part in msg_data:
        if isinstance(response_part, tuple):
            email_message = email.message_from_bytes(response_part[1])
            sender = email_message["From"]
            subject = email_message["Subject"]
            date = email_message["Date"]

            # Extract email body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = email_message.get_payload(decode=True).decode()

            # Send to Slack
            send_to_slack(subject, sender, date, body)

# Logout
mail.logout()
