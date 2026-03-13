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

@app.route('/api/run_offense', methods=['POST'])
def run_offense():
    """
    Triggers the generation of new phishing emails.
    """
    try:
        from src.main_orchestrator import run_experiment
        run_experiment()
        return jsonify({"status": "success"})
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

if __name__ == '__main__':
    # Ensure data dir exists
    os.makedirs("data", exist_ok=True)
    print("Dashboard starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
