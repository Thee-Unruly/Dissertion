# Quick Implementation Roadmap

## What Was Created For You

1. **Detection Config** (`src/config/detection_config.py`)
   - Adjustable thresholds for all detection methods
   - Pre-configured profiles: Aggressive, Balanced, Conservative

2. **Whitelist Manager** (`src/defense/whitelist.py`)
   - Add trusted senders/domains
   - Reduce false positives automatically

3. **Threshold Optimizer** (`src/defense/threshold_optimizer.py`)
   - A/B test different configurations
   - Compare precision, recall, F1 score, false positive rate

4. **Tuning Guide** (`TUNING_GUIDE.md`)
   - Complete step-by-step implementation

5. **Demo Script** (`test_tuning_example.py`)
   - Runnable examples of all tools

---

## Implementation Steps (Start Here!)

### Phase 1: Integration (1-2 hours)

#### Step 1: Update HeuristicAnalyzer
Replace the hardcoded weights in `src/defense/heuristic_analyzer.py`:

```python
# BEFORE (Old way - hardcoded)
score += min(len(urgency_hits) * 10, 30)

# AFTER (New way - configurable)
from src.config.detection_config import DETECTION_CONFIG
self.config = DETECTION_CONFIG["heuristic"]
score += min(len(urgency_hits) * self.config["urgency_weight"], 20)
```

#### Step 2: Update LLMClassifier
Add confidence filtering in `src/defense/llm_classifier.py`:

```python
# Add this in analyze() method:
confidence = result.get("confidence", 0.5)
if confidence < 0.6:  # From config
    result["risk_score"] = max(0, result["risk_score"] - 20)
```

#### Step 3: Update DetectorEngine
Add scoring logic to combine multiple detection methods.

---

### Phase 2: Testing (2-3 hours)

#### Step 4: Run the Demo
```bash
python test_tuning_example.py
```
This will show you:
- How whitelist works
- Different threshold configurations
- How to optimize

#### Step 5: Test Current System
Run your existing analysis pipeline and capture predictions:
```bash
python src/main_orchestrator.py
```

#### Step 6: Compare Configurations
Use ThresholdOptimizer to compare predictions against ground truth:
```python
from src.defense.threshold_optimizer import ThresholdOptimizer

optimizer = ThresholdOptimizer()
optimizer.evaluate_config(predictions, ground_truth, "Current")
optimizer.evaluate_config(predictions_adjusted, ground_truth, "Adjusted")
optimizer.compare_configs()
```

---

### Phase 3: Optimization (1-2 hours)

#### Step 7: Find Best Configuration
Start with these adjustments:

**If too many false positives:**
1. Reduce urgency_weight: 10 → 7
2. Reduce authority_weight: 5 → 3
3. Increase high_risk_threshold: 70 → 80
4. Increase LLM confidence_min: 0.6 → 0.7

**If missing too many attacks (false negatives):**
1. Increase urgency_weight: 10 → 12
2. Increase authority_weight: 5 → 7
3. Decrease high_risk_threshold: 70 → 60
4. Decrease LLM confidence_min: 0.6 → 0.5

#### Step 8: Add Trusted Senders
Edit `src/config/detection_config.py`:
```python
"whitelist": {
    "trusted_senders": [
        "hr@enron.com",
        "ceo@enron.com",
        "finance@enron.com",  # Add more here
    ]
}
```

---

## Key Metrics to Monitor

Track these as you adjust:

| Metric | Target | What It Means |
|--------|--------|---------------|
| **Precision** | > 90% | Of flagged emails, how many are really phishing? |
| **Recall** | > 85% | Of actual phishing, how many do we catch? |
| **False Positive Rate** | < 10% | Of legitimate emails, how many wrongly flagged? |
| **F1 Score** | > 0.85 | Balance between precision and recall |

---

## Configuration Files Reference

### Current Configuration (Balanced):

```python
DETECTION_CONFIG = {
    "heuristic": {
        "high_risk_threshold": 70,      # ← Increase to be less aggressive
        "medium_risk_threshold": 40,
        "urgency_weight": 5,            # ← Originally 10, reduced
        "authority_weight": 3,          # ← Originally 5, reduced
    },
    "llm": {
        "confidence_min": 0.6,          # ← Only trust confident predictions
    },
    "combined": {
        "heuristic_weight": 0.25,
        "llm_weight": 0.55,            # ← Trusting LLM more than heuristics
        "behavioral_weight": 0.20,
    }
}
```

### When to Use Each Profile:

- **CONFIG_AGGRESSIVE**: Testing phase, want to catch all possible phishing
- **CONFIG_BALANCED**: Production, good mix of detection and usability
- **CONFIG_CONSERVATIVE**: High-security environment, want minimal false positives

---

## Quick Debug Checklist

If your system is still too aggressive:

- [ ] Verify urgency_weight is set to 5 or lower
- [ ] Check high_risk_threshold is at 75+
- [ ] Ensure confidence_min filtering is enabled
- [ ] Review whitelist contains your trusted senders
- [ ] Check if behavioral analyzer is adding too much score

If system is missing attacks:

- [ ] Increase urgency_weight back to 7+
- [ ] Lower high_risk_threshold to 65
- [ ] Disable or reduce confidence filtering
- [ ] Check if important detection keywords are in URGENCY_KEYWORDS

---

## Example: Making ONE Change

Let's say you want to reduce false positives by 20%:

1. Open `src/config/detection_config.py`
2. Change:
   ```python
   "urgency_weight": 5,  # From 10
   ```
3. Run your test suite
4. Measure the change in false positive rate
5. Iterate: If still too many, reduce further or adjust threshold

---

## Testing Command

After making changes, test with:

```bash
python test_tuning_example.py
```

This will show you the impact of your configuration changes across different metrics.

---

## What's Next?

1. ✅ Run the demo to understand the tools
2. ✅ Make small configuration changes
3. ✅ Test against your ground truth data
4. ✅ Compare results with ThresholdOptimizer
5. ✅ Deploy the best configuration
6. ✅ Monitor metrics in production

**Estimated Total Time:** 4-6 hours for full implementation and optimization

Good luck! You're building a smarter, more balanced system! 🚀
