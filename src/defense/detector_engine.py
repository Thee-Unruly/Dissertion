import os
import json
import pandas as pd
from datetime import datetime
from src.defense.heuristic_analyzer import HeuristicAnalyzer
from src.defense.llm_classifier import LLMClassifier

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
            file_path = os.path.join(self.inbox_path, filename)
            with open(file_path, "r") as f:
                email_data = json.load(f)

            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            
            print(f"Analyzing: {subject[:50]}...")

            # 1. Heuristic Analysis
            h_results = self.heuristic_analyzer.analyze(subject, body)
            
            # 2. LLM Analysis (Optional)
            l_results = None
            if use_llm:
                l_results = self.llm_classifier.analyze(subject, body)

            # Combined Result
            entry = {
                "timestamp": datetime.now().isoformat(),
                "file": filename,
                "original_metadata": email_data.get("metadata", {}),
                "heuristics": h_results,
                "llm_analysis": l_results
            }
            
            # Simple voting logic for a final "Alert" decision
            h_score = h_results['score']
            l_score = l_results['risk_score'] if l_results else 0
            
            # Weigh LLM heavier if available
            combined_score = (h_score * 0.4 + l_score * 0.6) if use_llm else h_score
            entry["final_risk_score"] = combined_score
            entry["status"] = "ALERT" if combined_score >= 50 else "QUARANTINE" if combined_score >= 30 else "PASS"

            analysis_report.append(entry)
            self._log_result(entry)

        print(f"\nScan complete. Analyzed {len(analysis_report)} emails.")
        return analysis_report

    def _log_result(self, entry):
        os.makedirs(os.path.dirname(self.results_log), exist_ok=True)
        with open(self.results_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    # Test run (Heuristics only by default)
    detector = DetectorEngine()
    results = detector.scan_and_analyze(use_llm=False)
    
    if results:
        print("\n--- DETECTION SUMMARY ---")
        for r in results:
            print(f"File: {r['file']} | Score: {r['final_risk_score']} | Status: {r['status']}")
