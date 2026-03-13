import smtplib
import poplib
import email
import json
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class MailtrapBridge:
    """
    Connects the PhishDefense system to a real Mailtrap SMTP/POP3 gateway.
    Allows for Red Team injection and Blue Team scanning via real protocols.
    """
    
    def __init__(self):
        self.smtp_server = os.getenv("MAILTRAP_SMTP_SERVER", "sandbox.smtp.mailtrap.io")
        self.smtp_port = int(os.getenv("MAILTRAP_SMTP_PORT", "2525"))
        self.smtp_user = os.getenv("MAILTRAP_SMTP_USER")
        self.smtp_pass = os.getenv("MAILTRAP_SMTP_PASS")
        
        self.pop_server = os.getenv("MAILTRAP_POP_SERVER", "pop3.mailtrap.io")
        self.pop_port = int(os.getenv("MAILTRAP_POP_PORT", "9950")) # Safe SSL port
        self.pop_user = os.getenv("MAILTRAP_IMAP_USER") # Using same field for consistency
        self.pop_pass = os.getenv("MAILTRAP_IMAP_PASS")

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
        Connects to Mailtrap POP3, downloads messages, and saves them as JSON
        for the Blue Team's DetectorEngine to process.
        """
        if not self.pop_user or not self.pop_pass:
            print("Mailtrap POP3 credentials missing.")
            return []

        emails_synced = []
        try:
            # Connect using plain POP3 on port 1100
            mail = poplib.POP3(self.pop_server, 1100)
            mail.user(self.pop_user)
            mail.pass_(self.pop_pass)

            num_messages = len(mail.list()[1])
            os.makedirs(destination_dir, exist_ok=True)

            for i in range(num_messages):
                # Retrieve message (i+1 because POP3 is 1-indexed)
                resp, lines, octets = mail.retr(i + 1)
                msg_content = b'\n'.join(lines)
                msg = email.message_from_bytes(msg_content)
                
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
                    "metadata": {"source": "mailtrap_bridge_pop3"}
                }

                filename = f"mailtrap_pop3_{i+1}.json"
                with open(os.path.join(destination_dir, filename), "w") as f:
                    json.dump(email_json, f)
                
                emails_synced.append(filename)
                
                # Optional: Delete message after retrieval so we don't scan it twice
                # mail.dele(i + 1)
            
            mail.quit()
            print(f"Synced {len(emails_synced)} emails from Mailtrap POP3 gateway.")
            return emails_synced

        except Exception as e:
            print(f"POP3 Bridge Error: {e}")
            return []

if __name__ == "__main__":
    # Test connection
    bridge = MailtrapBridge()
    bridge.fetch_inbound_emails()
