# PhishDefense AI Hub 🛡️🤖

**An Advanced Adversarial Framework for Phishing Detection & Behavioral Analysis.**

This project is a scientific research platform designed for a dissertation on AI-driven cybersecurity. It implements a complete adversarial "loop"—generating sophisticated phishing attacks (Red Team) and evaluating them against a multi-layered defense system (Blue Team) using Large Language Models (LLMs) and behavioral communication patterns.

---

## 🚀 Key Features

### 1. Red Team (Adversarial Generation)
- **Spear Phishing Engine**: Generates highly personalized phishing emails based on real-world organizational data (Enron Corpus).
- **Tone Variations**: Automatically creates variations in attack styles (High Urgency, Low Urgency, Passive-Aggressive) to test detector sensitivity.
- **Context Awareness**: Leverages LLMs to craft realistic lures tailored to specific employee roles and projects.

### 2. Blue Team (Multi-Layer Defense)
- **Heuristic Analysis**: Rapid pattern-based flagging of common phishing indicators.
- **Behavioral Memory**: A specialized baseline module that tracks "normal" communication pairs within an organization to detect sender-recipient anomalies.
- **AI Reasoning**: Deep semantic analysis using LLMs (Groq/Llama-3) to detect social engineering tactics and subtle emotional manipulation.

### 3. Lab Evaluation Dashboard
- **Unified UI**: A modern, glassmorphic dashboard to visualize the entire attack/defense cycle.
- **Scientific Metrics**: Real-time calculation of Detection Rate, Accuracy, and Average Risk Scores.
- **Analysis Forensics**: Side-by-side view of the phishing content and the "thinking" process of the AI detector.

---

## 🛠️ Project Structure

```text
├── data/
│   ├── processed_enron.csv      # Organizational baseline data
│   ├── mock_inbox/              # Storage for 'delivered' phishing samples
│   └── behavioral_baseline.json # Pre-computed communication pairs
├── src/
│   ├── generation/              # Offensive (Red Team) modules
│   ├── defense/                 # Defensive (Blue Team) modules
│   │   ├── behavioral_baseline.py # The 'Behavioral Memory' engine
│   │   └── detector_engine.py     # Orchestrator for the defense stack
│   ├── dashboard_app.py         # Flask API for the UI
│   └── templates/               # UI HTML/JS code
├── evaluation/                  # Statistical reporting scripts
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- A [Groq API Key](https://console.groq.com/)

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

---

## 📈 Running the Experiment

1. **Start the Dashboard**:
   ```powershell
   $env:PYTHONPATH="."
   python src/dashboard_app.py
   ```
2. **Access the UI**: Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
3. **The Research Flow**:
   - **Step 1 (Offense)**: Click **"Generate Attacks"** to populate the research log.
   - **Step 2 (Defense)**: Click **"Defense Scan"** to trigger the AI-layered detection.
   - **Step 3 (Evaluation)**: View the **"Lab Evaluation"** tab for your dissertation statistics.

---

## 🔬 Scientific Contribution
This framework evaluates the **"Adversarial Gap"**—the difference between simple pattern-matching and deep semantic understanding. By integrating **Behavioral Memory**, the system moves beyond "blind" content analysis to understand the organizational context, making it significantly harder for attackers to bypass even with sophisticated AI-written lures.
