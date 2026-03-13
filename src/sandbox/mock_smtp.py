import os
import json
from datetime import datetime

class MockSMTP:
    """
    A simulated SMTP service for ethical sandboxing. 
    It 'delivers' emails by saving them to a local JSON/Maildir format 
    instead of sending them over the network.
    """
    def __init__(self, delivery_dir="data/mock_inbox/"):
        self.delivery_dir = delivery_dir
        if not os.path.exists(self.delivery_dir):
            os.makedirs(self.delivery_dir)
            print(f"Mock SMTP: Created delivery directory at {self.delivery_dir}")

    def deliver(self, sender, recipient, subject, body, metadata=None):
        """
        Intercepts an email and logs it to a local file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{recipient}_{timestamp}.json"
        
        email_data = {
            "from": sender,
            "to": recipient,
            "subject": subject,
            "body": body,
            "metadata": metadata,
            "delivered_at": datetime.now().isoformat()
        }
        
        filepath = os.path.join(self.delivery_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(email_data, f, indent=4)
        
        print(f"Mock SMTP: Email 'delivered' to {filepath}")
        return filepath

    def list_inbox(self):
        """
        Returns a list of all 'sent' emails in the sandbox.
        """
        files = [f for f in os.listdir(self.delivery_dir) if f.endswith(".json")]
        emails = []
        for file in files:
            with open(os.path.join(self.delivery_dir, file), "r", encoding="utf-8") as f:
                emails.append(json.load(f))
        return emails

if __name__ == "__main__":
    # Test Mock SMTP
    mock_server = MockSMTP()
    mock_server.deliver(
        "hr-compliance@enron.com", 
        "phillip.allen@enron.com", 
        "Required Security Update", 
        "Please click the link: http://secure.enron.net"
    )
