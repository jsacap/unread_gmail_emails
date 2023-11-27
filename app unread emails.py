import imaplib
import email
import getpass
import datetime
import re

# Keywords to search for in the "From" field (sender's name)
keywords = []

# Your Gmail credentials
imap_server = 'imap.gmail.com'
email_address = input('Enter your email address >>> ')
password = getpass.getpass('Enter your password >>> ')

# Regular expression pattern to match URLs
url_pattern = r'https?://\S+'

imap = imaplib.IMAP4_SSL(imap_server)
imap.login(email_address, password)

# Select the INBOX mailbox
imap.select('INBOX')

# Search for unread emails
search_criteria = f'(UNSEEN)'
status, data = imap.search(None, search_criteria)

# Get list of message IDs
message_ids = data[0].split()
# Modify this path
file_path = r''

# Create a file to save matching email content
with open(f'{file_path}\\all_emails.txt', 'a', encoding='utf-8') as all_emails_file:
    # Loop through the message IDs
    for message_id in message_ids:
        status, msg_data = imap.fetch(message_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        # Extract relevant information (subject, sender, date, body, etc.)
        subject = msg['subject']
        # Get sender's name and convert to lowercase
        sender_name = email.utils.parseaddr(msg['from'])[0].lower()
        date = msg['date']
        body = ""

        # Check if the sender's name contains any of the keywords
        if any(keyword.lower() in sender_name for keyword in keywords):
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        try:
                            body = part.get_payload(
                                decode=True).decode('utf-8')
                        except UnicodeDecodeError:
                            # Handle decoding errors by ignoring problematic characters
                            body = part.get_payload(
                                decode=True, errors='ignore').decode('utf-8')
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8')
                except UnicodeDecodeError:
                    # Handle decoding errors by ignoring problematic characters
                    body = msg.get_payload(
                        decode=True, errors='ignore').decode('utf-8')

            # Remove special characters and HTTP links from the email body
            # Remove special characters except . and ,
            body = re.sub(r'[^.,\w\s]', '', body)
            body = re.sub(url_pattern, '', body)  # Remove URLs

            # Remove words longer than 10 characters
            body = ' '.join([word for word in body.split() if len(word) <= 10])

            # Remove line breaks from the email body
            body = body.replace('\n', '').replace('\r', '')

            # Append the email content to the file
            all_emails_file.write(f"Subject: {subject}\n")
            all_emails_file.write(f"Date: {date}\n\n")
            all_emails_file.write(body)
            all_emails_file.write('\n\n\n')  # Add a separator between emails
        else:
            # If the criteria are not met, mark the email as unread
            imap.store(message_id, '-FLAGS', '(\Seen)')

# Close connection
imap.logout()
