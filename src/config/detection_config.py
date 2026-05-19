# Detection Configuration
# Adjust these values to fine-tune the system's sensitivity

DETECTION_CONFIG = {
    # ===== HEURISTIC ANALYZER =====
    "heuristic": {
        # Risk Level Thresholds
        "high_risk_threshold": 70,      # Score >= 70 → "High Risk" (Alert)
        "medium_risk_threshold": 40,    # Score >= 40 → "Medium Risk" (Quarantine)
        
        # Keyword Weights (REDUCED from original to be less aggressive)
        "urgency_weight": 5,            # Original: 10 per hit → Now: 5 per hit
        "authority_weight": 3,          # Original: 5 per hit → Now: 3 per hit
        
        # Link Weights
        "link_suspicious_weight": 40,   # Domain contains brand name but not official
        "link_ip_weight": 50,           # IP address instead of domain
        "link_untrusted_weight": 10,    # External domain
    },
    
    # ===== LLM CLASSIFIER =====
    "llm": {
        # Risk Level Thresholds
        "high_risk_threshold": 75,
        "medium_risk_threshold": 40,
        
        # Confidence Filtering
        "confidence_min": 0.6,          # Only trust LLM if confidence >= 0.6
                                         # Lower confidence → reduce score by 20 points
    },
    
    # ===== BEHAVIORAL BASELINE =====
    "behavioral": {
        "anomaly_score": 60,            # Score given for unseen sender-recipient pair
        "enabled": True,                # Toggle behavioral checks
    },
    
    # ===== COMBINED DETECTION WEIGHTS =====
    # Total should sum to 1.0
    "combined": {
        "heuristic_weight": 0.25,       # 25% from heuristics
        "llm_weight": 0.55,             # 55% from LLM (higher trust)
        "behavioral_weight": 0.20,      # 20% from behavioral
    },
    
    # ===== WHITELISTING =====
    "whitelist": {
        # Domains that should bypass stricter checks
        "trusted_domains": [
            "enron.com",
            "company.com",
        ],
        
        # Specific email addresses that are always trusted
        "trusted_senders": [
            "hr@enron.com",
            "it-support@enron.com",
            "admin@enron.com",
            "ceo@enron.com",
        ]
    },
    
    # ===== CLASSIFICATION MAPPING =====
    "classification": {
        "high_risk": "Alert",           # Present to user immediately
        "medium_risk": "Quarantine",    # Move to separate folder
        "low_risk": "Safe"              # Deliver to inbox
    }
}


# ===== EXAMPLE CONFIGURATIONS FOR TESTING =====
# Use these preset configurations to A/B test different strategies

CONFIG_AGGRESSIVE = {
    # Original aggressive configuration (High Detection, High False Positives)
    "heuristic": {
        "high_risk_threshold": 70,
        "medium_risk_threshold": 30,
        "urgency_weight": 10,
        "authority_weight": 5,
        "link_suspicious_weight": 40,
        "link_ip_weight": 50,
        "link_untrusted_weight": 10,
    },
    "llm": {"high_risk_threshold": 70, "confidence_min": 0.3},
    "combined": {"heuristic_weight": 0.4, "llm_weight": 0.4, "behavioral_weight": 0.2},
}

CONFIG_BALANCED = {
    # Balanced configuration (Moderate Detection, Moderate False Positives)
    "heuristic": {
        "high_risk_threshold": 75,
        "medium_risk_threshold": 45,
        "urgency_weight": 7,
        "authority_weight": 4,
        "link_suspicious_weight": 35,
        "link_ip_weight": 45,
        "link_untrusted_weight": 8,
    },
    "llm": {"high_risk_threshold": 75, "confidence_min": 0.5},
    "combined": {"heuristic_weight": 0.3, "llm_weight": 0.5, "behavioral_weight": 0.2},
}

CONFIG_CONSERVATIVE = {
    # Conservative configuration (Lower Detection, Lower False Positives)
    "heuristic": {
        "high_risk_threshold": 85,
        "medium_risk_threshold": 55,
        "urgency_weight": 3,
        "authority_weight": 2,
        "link_suspicious_weight": 30,
        "link_ip_weight": 40,
        "link_untrusted_weight": 5,
    },
    "llm": {"high_risk_threshold": 80, "confidence_min": 0.7},
    "combined": {"heuristic_weight": 0.2, "llm_weight": 0.6, "behavioral_weight": 0.2},
}


if __name__ == "__main__":
    print("Detection Configuration Loaded")
    print(f"High Risk Threshold: {DETECTION_CONFIG['heuristic']['high_risk_threshold']}")
    print(f"Urgency Weight: {DETECTION_CONFIG['heuristic']['urgency_weight']}")
