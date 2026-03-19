from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
import sys

# Add project root to path so we can import our modules
sys.path.append(os.getcwd())

from src.defense.detector_engine import DetectorEngine

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sandbox')
def sandbox():
    """renders the Gmail-style sandbox UI"""
    return render_template('sandbox.html')

@app.route('/api/results')
def get_results():
    results_file = "data/defense_analysis_v1.jsonl"
    data = []
    if os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except:
                    continue
    return jsonify(data)

@app.route('/api/offense_logs')
def get_offense_logs():
    offense_file = "data/generated_phishing_v1.jsonl"
    data = []
    if os.path.exists(offense_file):
        with open(offense_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except:
                    continue
    return jsonify(data)

@app.route('/api/inbox')
def get_inbox():
    """Lists raw emails in the mock inbox waiting for scanning."""
    inbox_dir = "data/mock_inbox/"
    emails = []
    if os.path.exists(inbox_dir):
        for filename in os.listdir(inbox_dir):
            if filename.endswith(".json"):
                with open(os.path.join(inbox_dir, filename), 'r') as f:
                    try:
                        mail = json.load(f)
                        emails.append({
                            "id": filename,
                            "sender": mail.get("sender"),
                            "subject": mail.get("subject"),
                            "body": mail.get("body", "")[:50] + "...",
                            "timestamp": mail.get("timestamp")
                        })
                    except:
                        continue
    return jsonify(emails)

@app.route('/api/run_offense', methods=['POST'])
def run_offense():
    """
    Triggers the generation of new phishing emails.
    Supports ?batch=X parameter for experiment control.
    """
    try:
        batch_size = request.args.get('batch', 1, type=int)
        
        # If batch > 1, use the detailed experiment script
        if batch_size > 1:
            from src.run_batch_experiment import run_named_batch
            run_named_batch(total_count=batch_size)
        else:
            from src.main_orchestrator import run_experiment
            run_experiment(limit_targets=1)
            
        return jsonify({"status": "success", "batch": batch_size})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/run_scan', methods=['POST'])
def run_scan():
    """
    Triggers the detection pipeline.
    """
    try:
        # We'll use the DetectorEngine class directly
        # use_llm=True for a full evaluation
        detector = DetectorEngine()
        results = detector.scan_and_analyze(use_llm=True)
        return jsonify({"status": "success", "analyzed": len(results)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/export_report')
def export_report():
    """
    Generates a structured text report for dissertation purposes.
    """
    results_file = "data/defense_analysis_v1.jsonl"
    if not os.path.exists(results_file):
        return "No results found. Please run a scan first.", 404
        
    data = []
    with open(results_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
            
    if not data:
        return "Log file is empty.", 404

    total = len(data)
    alerts = len([d for d in data if d['status'] == 'ALERT'])
    quarantine = len([d for d in data if d['status'] == 'QUARANTINE'])
    pass_count = len([d for d in data if d['status'] == 'PASS'])
    avg_risk = sum([d['final_risk_score'] for d in data]) / total
    
    report = f"--- PHISH-DEFENSE AI LAB REPORT ---\n"
    report += f"Generated on: {data[-1]['timestamp']}\n\n"
    report += f"[SUMMARY STATISTICS]\n"
    report += f"- Total Samples: {total}\n"
    report += f"- Detection Accuracy: {((alerts + quarantine) / total * 100):.1f}%\n"
    report += f"- Average Risk Score: {avg_risk:.1f}\n\n"
    report += f"[DETECTION BREAKDOWN]\n"
    report += f"- Alerts (High Risk): {alerts}\n"
    report += f"- Quarantine (Suspicious): {quarantine}\n"
    report += f"- False Negatives (Miss): {pass_count}\n\n"
    report += f"[DETAILED AUDIT LOG]\n"
    
    for entry in data:
        report += f"[{entry['status']}] File: {entry['file']}\n"
        report += f"   Sender: {entry['sender']} -> Recipient: {entry['recipient']}\n"
        report += f"   Final Risk Score: {entry['final_risk_score']}\n"
        report += f"   Heuristics: {', '.join(entry['heuristics']['findings'][:2])}...\n"
        if entry.get('llm_analysis'):
            report += f"   LLM Logic: {entry['llm_analysis']['analysis'][:100]}...\n"
        report += "-"*50 + "\n"
        
    return report, 200, {'Content-Type': 'text/plain', 'Content-Disposition': 'attachment; filename=dissertation_lab_report.txt'}

if __name__ == '__main__':
    # Ensure data dir exists
    os.makedirs("data", exist_ok=True)
    print("Dashboard starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
