import pandas as pd
import os
import json

class BehavioralBaseline:
    """
    Creates a baseline of 'Normal' organizational behavior from Enron data.
    """
    
    def __init__(self, processed_data_path="data/processed_enron.csv"):
        self.processed_data_path = processed_data_path
        self.baseline_file = "data/behavioral_baseline.json"
        self.relationships = set()
        
        if os.path.exists(self.baseline_file):
            self.load_baseline()
        else:
            self.build_baseline()

    def build_baseline(self):
        """
        Parses processed Enron data to extract (From, To) valid relationships.
        """
        if not os.path.exists(self.processed_data_path):
            print(f"Error: {self.processed_data_path} not found. Cannot build baseline.")
            return

        print("Building Behavioral Baseline from Enron data...")
        df = pd.read_csv(self.processed_data_path)
        
        # Clean up and normalize email addresses
        for idx, row in df.iterrows():
            sender = str(row.get('From', '')).lower().strip()
            recipient = str(row.get('To', '')).lower().strip()
            
            if sender and recipient:
                # Handle multiple recipients
                recipients = [r.strip() for r in recipient.split(',')]
                for r in recipients:
                    self.relationships.add((sender, r))

        # Save to JSON for faster loading next time
        serializable_relationships = [list(rel) for rel in self.relationships]
        os.makedirs(os.path.dirname(self.baseline_file), exist_ok=True)
        with open(self.baseline_file, 'w') as f:
            json.dump(serializable_relationships, f)
        print(f"Baseline built with {len(self.relationships)} unique relationships.")

    def load_baseline(self):
        with open(self.baseline_file, 'r') as f:
            data = json.load(f)
            self.relationships = set(tuple(rel) for rel in data)
        print(f"Baseline loaded from disk ({len(self.relationships)} relationships).")

    def check_relationship(self, sender, recipient):
        """
        Returns True if the relationship has been seen before in the baseline.
        """
        sender = str(sender).lower().strip()
        recipient = str(recipient).lower().strip()
        
        # Exact match
        if (sender, recipient) in self.relationships:
            return 1.0 # Normal
        
        # Partial match (domain level or similar)
        # We can expand this later, for now we stick to strict behavioral pairs
        return 0.0 # Anomaly

if __name__ == "__main__":
    # Test
    baseline = BehavioralBaseline()
    print(f"Check wellness: {baseline.check_relationship('wellness@enron.com', 'employees@enron.com')}")
