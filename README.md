# mail2slack
# Email to Slack Forwarder

This script checks your email inbox for new messages and forwards them to a specified Slack channel via an Incoming Webhook. It’s ideal for staying updated on important emails without checking your inbox constantly.

## Features
- Fetches unread emails from your inbox.
- Extracts key details: sender, subject, and body.
- Sends the details to a Slack channel.

## Prerequisites
- An email account with IMAP access.
- A Slack Incoming Webhook URL.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/email-to-slack-forwarder.git
   cd email-to-slack-forwarder
