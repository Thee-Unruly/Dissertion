import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.defense.heuristic_analyzer import HeuristicAnalyzer
from src.defense.llm_classifier import LLMClassifier
from src.defense.behavioral_baseline import BehavioralBaseline

class DetectorEngine:
    """
    Orchestrates the defensive pipeline: 
    - Scans the mock inbox
    - Analyzes each email using heuristics and LLM
    - Generates a security report
    """
    
    def __init__(self, inbox_path="data/mock_inbox/", target_domain="enron.com"):
        self.inbox_path = inbox_path
        self.target_domain = target_domain
        self.heuristic_analyzer = HeuristicAnalyzer(target_domain=target_domain)
        self.behavioral_baseline = BehavioralBaseline()
        # We'll initialize LLM classifier only if needed to save tokens during testing
        self.llm_classifier = None 
        self.results_log = "data/defense_analysis_v1.jsonl"

    def scan_and_analyze(self, use_llm=False):
        """
        Processes all emails in the mock inbox.
        """
        print(f"--- STARTING DEFENSIVE SCAN on {self.inbox_path} ---")
        
        if not os.path.exists(self.inbox_path):
            print(f"Error: Inbox path {self.inbox_path} does not exist.")
            return []

        if use_llm and not self.llm_classifier:
            self.llm_classifier = LLMClassifier()

        files = [f for f in os.listdir(self.inbox_path) if f.endswith(".json")]
        if not files:
            print("No emails found in inbox.")
            return []

        print(f"Found {len(files)} samples to analyze...")
        
        analysis_report = []

        for filename in files:
            try:
                file_path = os.path.join(self.inbox_path, filename)
                with open(file_path, "r") as f:
                    email_data = json.load(f)

                # Ensure string types for analysis to avoid subscriptable errors
                subject = str(email_data.get("subject", ""))
                body = str(email_data.get("body", ""))
                
                print(f"Analyzing: {subject[:50]}...")

                # 1. Heuristic Analysis
                h_results = self.heuristic_analyzer.analyze(subject, body)
                
                # 2. Behavioral Analysis
                sender = str(email_data.get("sender", "unknown"))
                recipient = str(email_data.get("recipient", "unknown"))
                is_normal = self.behavioral_baseline.check_relationship(sender, recipient)
                
                bh_score = 0 if is_normal == 1.0 else 60 
                bh_finding = f"Behavioral Anomaly: Unseen communication pair ({sender} -> {recipient})" if bh_score > 0 else "Normal: Established communication pair."

                # 3. LLM Analysis (Optional)
                l_results = None
                if use_llm:
                    import time
                    time.sleep(1.5) # Sleep to avoid rate limit
                    l_results = self.llm_classifier.analyze(subject, body)

                # Combined Result
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "file": filename,
                    "sender": sender,
                    "recipient": recipient,
                    "subject": subject,
                    "body": body,
                    "original_metadata": email_data.get("metadata", {}),
                    "heuristics": h_results,
                    "behavioral": {
                        "score": bh_score,
                        "finding": bh_finding
                    },
                    "llm_analysis": l_results
                }
                
                h_score = h_results['score']
                l_score = l_results['risk_score'] if l_results else 0
                
                if use_llm:
                    combined_score = (h_score * 0.3 + bh_score * 0.3 + l_score * 0.4)
                else:
                    combined_score = (h_score * 0.5 + bh_score * 0.5)
                
                entry["final_risk_score"] = min(combined_score, 100)
                entry["status"] = "ALERT" if combined_score >= 50 else "QUARANTINE" if combined_score >= 30 else "PASS"

                analysis_report.append(entry)
                self._log_result(entry)
            except Exception as loop_e:
                print(f"Skipping malformed file {filename}: {loop_e}")
                continue

        print(f"\nScan complete. Analyzed {len(analysis_report)} emails.")
        return analysis_report

    def _log_result(self, entry):
        os.makedirs(os.path.dirname(self.results_log), exist_ok=True)
        with open(self.results_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    # Test run (Enabling LLM for full evaluation)
    detector = DetectorEngine()
    results = detector.scan_and_analyze(use_llm=True)
    
    if results:
        print("\n--- DETECTION SUMMARY ---")
        for r in results:
            print(f"File: {r['file']} | Score: {r['final_risk_score']} | Status: {r['status']}")
