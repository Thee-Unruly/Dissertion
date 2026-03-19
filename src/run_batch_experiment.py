import os
import sys
import json
import pandas as pd
import random
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.generation.phishing_generator import PhishingGenerator
from src.generation.url_obfuscator import generate_obfuscated_url

def run_named_batch(phish_count=5, benign_count=5, inbox_dir="data/mock_inbox/"):
    """
    Generates a balanced batch of emails for testing.
    - phish_count: Number of AI-generated phishing emails.
    - benign_count: Number of real Enron emails to use as 'good' samples.
    """
    os.makedirs(inbox_dir, exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Load Enron data for samples
    df = pd.read_csv("data/processed_enron.csv")
    
    generator = PhishingGenerator(model_name="llama-3.3-70b-versatile")
    ground_truth = {}
    
    # Load existing ground truth if it exists
    if os.path.exists("data/ground_truth.json"):
        with open("data/ground_truth.json", "r") as f:
            ground_truth = json.load(f)

    # 1. Generate Phishing Emails
    print(f"Generating {phish_count} phishing samples...")
    phish_targets = df.sample(n=phish_count)
    tones = ["High Urgency", "Low Urgency", "Passive-Aggressive"]
    
    for _, row in phish_targets.iterrows():
        tone = random.choice(tones)
        target_name = row['X-From'].split('<')[0].strip()
        phishing_url = generate_obfuscated_url("enron.com")
        
        params = {
            "target_name": target_name,
            "organization": "Enron Corp",
            "role": "Employee",
            "context": f"Regarding your recent email about {row['Subject']}",
            "tone_style": tone,
            "phishing_link": phishing_url
        }
        
        body = generator.generate("spear_phishing", params)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"phish_{timestamp}.json"
        
        email_data = {
            "sender": "security-alerts@enron-internal.com",
            "recipient": row['To'],
            "subject": f"Security Update: {row['Subject']}",
            "body": body,
            "timestamp": timestamp,
            "metadata": {"type": "phishing", "tone": tone}
        }
        
        with open(os.path.join(inbox_dir, filename), "w") as f:
            json.dump(email_data, f)
        
        ground_truth[filename] = "malicious"

    # 2. Sample Benign Emails
    print(f"Sampling {benign_count} benign emails...")
    benign_samples = df.sample(n=benign_count)
    
    for _, row in benign_samples.iterrows():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"benign_{timestamp}.json"
        
        email_data = {
            "sender": row['X-From'],
            "recipient": row['To'],
            "subject": row['Subject'],
            "body": row['Body'],
            "timestamp": timestamp,
            "metadata": {"type": "benign"}
        }
        
        with open(os.path.join(inbox_dir, filename), "w") as f:
            json.dump(email_data, f)
        
        ground_truth[filename] = "benign"

    # Save Ground Truth
    with open("data/ground_truth.json", "w") as f:
        json.dump(ground_truth, f, indent=4)
        
    print(f"Batch generation complete. 10 emails added to {inbox_dir}")

if __name__ == "__main__":
    run_named_batch(5, 5)
