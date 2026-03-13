import pandas as pd
import random
import os
from src.generation.phishing_generator import PhishingGenerator
from src.sandbox.mock_smtp import MockSMTP
from src.sandbox.mailtrap_bridge import MailtrapBridge
from src.generation.url_obfuscator import generate_obfuscated_url

def run_experiment(limit_targets=2):
    """
    Enhanced Orchestrator: 
    - Generates 3 variations per target (Low, High, Passive-Aggressive).
    - Uses obfuscated URLs for realism.
    """
    print("--- STARTING ENHANCED DISSERTATION EXPERIMENT ---")
    
    mode = os.getenv("GATEWAY_MODE", "MOCK")
    print(f"Operational Mode: {mode}")

    if not os.path.exists("data/processed_enron.csv"):
        print("Error: data/processed_enron.csv not found.")
        return
        
    df = pd.read_csv("data/processed_enron.csv")
    targets = df.dropna(subset=['X-From', 'Date', 'Subject', 'Body']).sample(n=limit_targets)
    
    generator = PhishingGenerator(model_name="llama-3.3-70b-versatile")
    
    # Select bridge based on mode
    if mode == "MAILTRAP":
        bridge = MailtrapBridge()
    else:
        bridge = MockSMTP()

    tones = ["Low Urgency", "High Urgency", "Passive-Aggressive"]

    print(f"Targeting {len(targets)} personas with {len(tones)} variations each...")
    
    for idx, target in targets.iterrows():
        target_name = target['X-From'].split('<')[0].strip()
        org = "Enron Corporation"
        context = f"Internal email regarding: {target['Subject']}"
        
        # 1. Generate Obfuscated URL once per target (or per variation if preferred)
        phishing_url = generate_obfuscated_url("enron.com")

        for tone in tones:
            params = {
                "target_name": target_name,
                "organization": org,
                "role": "Enron Employee",
                "context": context,
                "tone_style": tone,
                "phishing_link": phishing_url
            }
            
            print(f"\n[Target: {target_name}] Generating variation: {tone}...")
            generated_email_text = generator.generate("spear_phishing", params)
            
            if generated_email_text:
                subject = f"[{tone}] " + params['context']
                if "Subject:" in generated_email_text:
                    parts = generated_email_text.split("Body:", 1)
                    subject = parts[0].replace("Subject:", "").strip()
                    body = parts[1].strip() if len(parts) > 1 else generated_email_text
                else:
                    body = generated_email_text
                
                recipient = target['To'] if pd.notnull(target['To']) else f"{target_name}@enron.local"
                
                if mode == "MAILTRAP":
                    bridge.send_attack(
                        sender="internal-alert@enron-security.local",
                        recipient=recipient,
                        subject=subject,
                        body=body
                    )
                else:
                    bridge.deliver(
                        sender="internal-alert@enron-security.local",
                        recipient=recipient,
                        subject=subject,
                        body=body,
                        metadata={
                            "attack_type": "spear_phishing", 
                            "tone": tone,
                            "url_style": "obfuscated",
                            "source_enron_msg": target['file']
                        }
                    )

    if mode == "MAILTRAP":
        print("\n--- SYNCING INBOUND FROM MAILTRAP (Blue Team View) ---")
        bridge.fetch_inbound_emails()

    print("\n--- ENHANCED EXPERIMENT COMPLETED ---")
    print(f"Check {'data/mock_inbox/' if mode == 'MOCK' else 'Mailtrap UI'} for the results.")

if __name__ == "__main__":
    run_experiment()
