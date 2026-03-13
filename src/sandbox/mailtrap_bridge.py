import smtplib
import imaplib
import email
import json
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class MailtrapBridge:
    """
    Connects the PhishDefense system to a real Mailtrap SMTP/IMAP gateway.
    Allows for Red Team injection and Blue Team scanning via real protocols.
    """
    
    def __init__(self):
        self.smtp_server = os.getenv("MAILTRAP_SMTP_SERVER", "sandbox.smtp.mailtrap.io")
        self.smtp_port = int(os.getenv("MAILTRAP_SMTP_PORT", "2525"))
        self.smtp_user = os.getenv("MAILTRAP_SMTP_USER")
        self.smtp_pass = os.getenv("MAILTRAP_SMTP_PASS")
        
        self.imap_server = os.getenv("MAILTRAP_IMAP_SERVER", "sandbox.imap.mailtrap.io")
        self.imap_user = os.getenv("MAILTRAP_IMAP_USER")
        self.imap_pass = os.getenv("MAILTRAP_IMAP_PASS")

    def send_attack(self, sender, recipient, subject, body):
        """
        Sends a generated phishing email via Mailtrap SMTP.
        """
        if not self.smtp_user or not self.smtp_pass:
            print("Mailtrap credentials missing. Check your .env file.")
            return False

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(sender, [recipient], msg.as_string())
            print(f"Attack relayed successfully to Mailtrap: {subject}")
            return True
        except Exception as e:
            print(f"SMTP Bridge Error: {e}")
            return False

    def fetch_inbound_emails(self, destination_dir="data/mock_inbox/"):
        """
        Connects to Mailtrap IMAP, downloads recent messages, and saves them as JSON
        for the Blue Team's DetectorEngine to process.
        """
        if not self.imap_user or not self.imap_pass:
            print("Mailtrap IMAP credentials missing.")
            return []

        emails_synced = []
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.imap_user, self.imap_pass)
            mail.select("inbox")

            status, messages = mail.search(None, 'ALL')
            mail_ids = messages[0].split()

            os.makedirs(destination_dir, exist_ok=True)

            for m_id in mail_ids:
                status, data = mail.fetch(m_id, '(RFC822)')
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg['subject']
                        sender = msg['from']
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        # Convert to our detector format
                        email_json = {
                            "sender": sender,
                            "recipient": msg['to'],
                            "subject": subject,
                            "body": body,
                            "metadata": {"source": "mailtrap_bridge"}
                        }

                        filename = f"mailtrap_{m_id.decode()}.json"
                        with open(os.path.join(destination_dir, filename), "w") as f:
                            json.dump(email_json, f)
                        
                        emails_synced.append(filename)
            
            mail.logout()
            print(f"Synced {len(emails_synced)} emails from Mailtrap gateway.")
            return emails_synced

        except Exception as e:
            print(f"IMAP Bridge Error: {e}")
            return []

if __name__ == "__main__":
    # Test connection
    bridge = MailtrapBridge()
    bridge.fetch_inbound_emails()
