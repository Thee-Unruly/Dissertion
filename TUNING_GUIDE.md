# Phishing Detection System Tuning Guide

## Overview
Your system uses three detection layers (Heuristics, LLM, Behavioral). This guide helps you reduce false positives while maintaining detection accuracy.

---

## Step 1: Understand Current Performance

### What You Have
- **Heuristic Analyzer**: Checks for urgency keywords, authority language, and suspicious links
- **LLM Classifier**: Analyzes phishing intent with risk scores (0-100)
- **Behavioral Baseline**: Flags unusual sender-recipient pairs
- **Detection Engine**: Combines all three

### Current Issue
Your system is **aggressive** (high false positives). You need to:
1. Increase confidence thresholds
2. Reduce keyword sensitivity
3. Add whitelist exceptions
4. Fine-tune scoring weights

---

## Step 2: Implement Adjustable Thresholds

### 2.1 Create a Configuration File

Create `src/config/detection_config.py`:

```python
# Detection Thresholds Configuration
DETECTION_CONFIG = {
    # Heuristic Scoring Thresholds
    "heuristic": {
        "high_risk_threshold": 70,      # Change from default
        "medium_risk_threshold": 40,
        "urgency_weight": 10,           # Reduced from 10 per hit
        "authority_weight": 5,          # Reduced from 5 per hit
        "link_suspicious_weight": 40,
        "link_ip_weight": 50,
        "link_untrusted_weight": 10,
    },
    
    # LLM Scoring Thresholds
    "llm": {
        "high_risk_threshold": 75,
        "medium_risk_threshold": 40,
        "confidence_min": 0.6,          # Only trust LLM if confident
    },
    
    # Behavioral Thresholds
    "behavioral": {
        "anomaly_score": 60,            # Flag unusual sender pairs
        "enabled": True,
    },
    
    # Combined Detection
    "combined": {
        "heuristic_weight": 0.3,        # 30% heuristics
        "llm_weight": 0.5,              # 50% LLM analysis
        "behavioral_weight": 0.2,       # 20% behavioral
    },
    
    # Whitelist & Exceptions
    "whitelist": {
        "trusted_domains": [
            "enron.com",
            "company.com",
            "partner.com"
        ],
        "trusted_senders": [
            "hr@enron.com",
            "it-support@enron.com",
            "admin@enron.com"
        ]
    }
}
```

---

## Step 3: Modify HeuristicAnalyzer

### 3.1 Make It Configurable

Edit `src/defense/heuristic_analyzer.py`:

```python
import re
from urllib.parse import urlparse
from src.config.detection_config import DETECTION_CONFIG

class HeuristicAnalyzer:
    """
    Analyzes email content for common heuristic phishing indicators.
    Now with configurable thresholds.
    """
    
    URGENCY_KEYWORDS = [
        r"urgent", r"immediate", r"action required", r"suspension", r"expired",
        r"unauthorized", r"security alert", r"critical", r"verify your account",
        r"compromised", r"attention", r"failure to comply"
    ]
    
    AUTHORITY_KEYWORDS = [
        r"compliance", r"policy", r"human resources", r"it department",
        r"management", r"strictly prohibited", r"mandatory", r"legal action"
    ]

    def __init__(self, target_domain="enron.com", config=None):
        self.target_domain = target_domain.lower()
        self.brand_name = target_domain.split('.')[0].lower()
        self.config = config or DETECTION_CONFIG["heuristic"]

    def analyze(self, subject, body):
        """
        Runs multiple heuristic checks with configurable weights.
        """
        findings = []
        score = 0
        
        # 1. Urgency Detection (REDUCED WEIGHT)
        urgency_hits = self._check_keywords(subject + " " + body, self.URGENCY_KEYWORDS)
        if urgency_hits:
            findings.append(f"Urgency/Pressure detected: {', '.join(urgency_hits)}")
            # Use configurable weight instead of hardcoded 10
            score += min(len(urgency_hits) * self.config["urgency_weight"], 20)
            
        # 2. Authority/Policy Language (REDUCED WEIGHT)
        auth_hits = self._check_keywords(body, self.AUTHORITY_KEYWORDS)
        if auth_hits:
            findings.append(f"Authority-based language detected: {', '.join(auth_hits)}")
            # Use configurable weight instead of hardcoded 5
            score += min(len(auth_hits) * self.config["authority_weight"], 15)
            
        # 3. Link Analysis
        links = self._extract_links(body)
        for link in links:
            link_score, link_finding = self._analyze_link(link)
            if link_score > 0:
                score += link_score
                findings.append(link_finding)

        # Normalize score (Cap at 100)
        final_score = min(score, 100)
        
        # Determine risk level using configurable thresholds
        high_threshold = self.config["high_risk_threshold"]
        medium_threshold = self.config["medium_risk_threshold"]
        
        if final_score >= high_threshold:
            risk_level = "High"
        elif final_score >= medium_threshold:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "score": final_score,
            "risk_level": risk_level,
            "findings": findings
        }

    def _check_keywords(self, text, keywords):
        text = text.lower()
        found = []
        for kw in keywords:
            if re.search(r'\b' + kw + r'\b', text):
                found.append(kw)
        return found

    def _extract_links(self, text):
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

    def _analyze_link(self, link):
        try:
            parsed = urlparse(link)
            domain = parsed.netloc.lower()
            
            # Case 1: Domain is the exact target domain (Safe)
            if domain == self.target_domain or domain.endswith("." + self.target_domain):
                return 0, ""

            # Case 2: Domain contains brand name but isn't official (SSO spoofing)
            if self.brand_name in domain:
                return self.config["link_suspicious_weight"], \
                       f"Suspicious Link: Domain '{domain}' contains '{self.brand_name}' but is not '{self.target_domain}'"
            
            # Case 3: IP Address as domain
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
                return self.config["link_ip_weight"], \
                       f"Critical Link: Uses IP address instead of domain: {domain}"
                
            return self.config["link_untrusted_weight"], \
                   f"Untrusted Link: External domain detected: {domain}"
        except Exception:
            return 5, "Malformed Link detected"
```

---

## Step 4: Modify LLMClassifier

### 4.1 Add Confidence Filtering

Edit `src/defense/llm_classifier.py`:

```python
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from src.config.detection_config import DETECTION_CONFIG

load_dotenv(os.path.join(os.getcwd(), '.env'))

class LLMClassifier:
    """
    Uses LLM reasoning to detect social engineering and phishing intent.
    Now with confidence-based filtering.
    """
    
    DETECTION_PROMPT = """
    You are a Senior Cybersecurity Threat Analyst specializing in Social Engineering detection.
    Analyze the following email and determine if it is a phishing attempt.
    
    --- EMAIL START ---
    Subject: {subject}
    Content: {body}
    --- EMAIL END ---
    
    Evaluate based on:
    1. Psychological Triggers: (Fear, Urgency, Curiosity, Authority, Greed).
    2. Contextual Anomalies: Does the request make sense in a corporate environment?
    3. Call to Action: Is there a suspicious link or request for sensitive info?
    
    Return your analysis strictly in the following JSON format:
    {{
        "risk_score": (int from 0 to 100),
        "risk_level": "(Low/Medium/High)",
        "confidence": (float from 0 to 1, how confident are you),
        "analysis": "(Brief explanation of why it is or isn't phishing)",
        "detected_tactics": ["tactic1", "tactic2"]
    }}
    """

    def __init__(self, model_name=None, config=None):
        if model_name is None:
            model_name = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.1
        )
        self.prompt = PromptTemplate(
            input_variables=["subject", "body"],
            template=self.DETECTION_PROMPT
        )
        self.chain = self.prompt | self.llm
        self.config = config or DETECTION_CONFIG["llm"]

    def analyze(self, subject, body):
        """
        Runs LLM analysis with confidence filtering.
        """
        import time
        max_retries = 3
        delay = 5
        
        for attempt in range(max_retries):
            try:
                response = self.chain.invoke({"subject": subject, "body": body})
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                if "{" in response_text and "}" in response_text:
                    json_str = response_text[response_text.find("{"):response_text.rfind("}")+1]
                    result = json.loads(json_str)
                    
                    # ADD CONFIDENCE FILTERING
                    confidence = result.get("confidence", 0.5)
                    if confidence < self.config["confidence_min"]:
                        # If LLM is not confident, downgrade the result
                        result["risk_score"] = max(0, result["risk_score"] - 20)
                        result["confidence_adjustment"] = "Downgraded due to low confidence"
                    
                    return result
                break
            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    print(f"   ! Rate limited. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                print(f"LLM Classification Error: {e}")
                
        return {
            "risk_score": 0,
            "risk_level": "Error",
            "confidence": 0,
            "analysis": "LLM failed or rate limited.",
            "detected_tactics": []
        }
```

---

## Step 5: Add Whitelisting

### 5.1 Create a Whitelist Module

Create `src/defense/whitelist.py`:

```python
from src.config.detection_config import DETECTION_CONFIG

class WhitelistManager:
    """
    Manages trusted senders and domains to reduce false positives.
    """
    
    def __init__(self, config=None):
        self.config = config or DETECTION_CONFIG["whitelist"]
        self.trusted_domains = set(self.config["trusted_domains"])
        self.trusted_senders = set(self.config["trusted_senders"])
    
    def is_from_trusted_domain(self, email_address):
        """Check if email is from a trusted domain."""
        if "@" not in email_address:
            return False
        domain = email_address.split("@")[1].lower()
        return domain in self.trusted_domains
    
    def is_trusted_sender(self, email_address):
        """Check if the exact sender is trusted."""
        return email_address.lower() in self.trusted_senders
    
    def should_skip_aggressive_checks(self, sender):
        """
        Return True if email should skip aggressive heuristic checks.
        Trusted senders can still be analyzed but with less aggressive scoring.
        """
        return self.is_from_trusted_domain(sender) or self.is_trusted_sender(sender)
```

---

## Step 6: Implement Ensemble Scoring

### 6.1 Modify DetectorEngine

Add weighted scoring to your detector engine. Edit the scoring logic in `src/defense/detector_engine.py`:

```python
def _calculate_combined_score(self, heuristic_result, llm_result, behavioral_result, config=None):
    """
    Combines scores from all three detection methods using configurable weights.
    """
    config = config or DETECTION_CONFIG["combined"]
    
    h_score = heuristic_result.get("score", 0)
    l_score = llm_result.get("risk_score", 0) if llm_result else 0
    b_score = behavioral_result.get("score", 0) if behavioral_result else 0
    
    # Weighted combination
    combined_score = (
        (h_score * config["heuristic_weight"]) +
        (l_score * config["llm_weight"]) +
        (b_score * config["behavioral_weight"])
    )
    
    return min(combined_score, 100)

def _classify_email(self, combined_score):
    """
    Classify email based on combined score using configurable thresholds.
    """
    high_threshold = DETECTION_CONFIG["heuristic"]["high_risk_threshold"]
    medium_threshold = DETECTION_CONFIG["heuristic"]["medium_risk_threshold"]
    
    if combined_score >= high_threshold:
        return "Alert"
    elif combined_score >= medium_threshold:
        return "Quarantine"
    else:
        return "Safe"
```

---

## Step 7: A/B Testing Strategy

### 7.1 Create a Testing Module

Create `src/defense/threshold_optimizer.py`:

```python
import json
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

class ThresholdOptimizer:
    """
    Tests different threshold configurations to find optimal balance.
    """
    
    def __init__(self):
        self.results = {}
    
    def evaluate_config(self, predictions, ground_truth, config_name):
        """
        Evaluate a configuration against ground truth.
        """
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, average='binary'
        )
        
        tn, fp, fn, tp = confusion_matrix(ground_truth, predictions).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        self.results[config_name] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "false_positive_rate": fpr,
            "false_negatives": fn,
            "true_positives": tp
        }
        
        return self.results[config_name]
    
    def compare_configs(self):
        """Print comparison of all tested configurations."""
        print("\n=== THRESHOLD OPTIMIZATION RESULTS ===\n")
        for config_name, metrics in self.results.items():
            print(f"Config: {config_name}")
            print(f"  Precision: {metrics['precision']:.3f}")
            print(f"  Recall: {metrics['recall']:.3f}")
            print(f"  F1 Score: {metrics['f1']:.3f}")
            print(f"  False Positive Rate: {metrics['false_positive_rate']:.3f}")
            print(f"  False Negatives: {metrics['false_negatives']}")
            print()
```

---

## Step 8: Implementation Checklist

- [ ] Create `src/config/detection_config.py`
- [ ] Update `src/defense/heuristic_analyzer.py` with configurable weights
- [ ] Update `src/defense/llm_classifier.py` with confidence filtering
- [ ] Create `src/defense/whitelist.py`
- [ ] Update `src/defense/detector_engine.py` with ensemble scoring
- [ ] Create `src/defense/threshold_optimizer.py`
- [ ] Test with current dataset
- [ ] Measure precision, recall, and false positive rate
- [ ] Iterate on thresholds

---

## Step 9: Testing & Iteration

### 9.1 Test Script

Create `test_tuning.py`:

```python
import json
from src.defense.detector_engine import DetectorEngine
from src.defense.threshold_optimizer import ThresholdOptimizer
from src.config.detection_config import DETECTION_CONFIG

# Load ground truth
with open("data/ground_truth.json", "r") as f:
    ground_truth = json.load(f)

# Initialize detector and optimizer
detector = DetectorEngine()
optimizer = ThresholdOptimizer()

# Test different configurations
configs_to_test = [
    {"name": "Default", "h_threshold": 70, "l_threshold": 75},
    {"name": "Reduced Aggression", "h_threshold": 80, "l_threshold": 80},
    {"name": "Confidence-Based", "h_threshold": 75, "l_threshold": 70},
]

for test_config in configs_to_test:
    predictions = []
    # Run detector with modified thresholds
    results = detector.scan_and_analyze(use_llm=True)
    
    # Evaluate and store results
    optimizer.evaluate_config(predictions, ground_truth, test_config["name"])

optimizer.compare_configs()
```

---

## Step 10: Key Metrics to Monitor

1. **Precision**: Of emails flagged as phishing, how many actually are?
2. **Recall**: Of actual phishing emails, how many did we catch?
3. **False Positive Rate**: How many legitimate emails are incorrectly flagged?
4. **F1 Score**: Balance between precision and recall

**Target Metrics**:
- Precision: > 90% (avoid false flagging legitimate emails)
- Recall: > 85% (catch most phishing emails)
- FPR: < 10% (minimize user frustration)

---

## Quick Start

1. **Copy** `detection_config.py` template above
2. **Update** your heuristic analyzer to use config
3. **Add** confidence filtering to LLM
4. **Run** tests with different thresholds
5. **Compare** results and adjust

Start by reducing urgency and authority weights by 50%, then test!
