"""
Quick Start: Testing Tuning Configurations
This script demonstrates how to use the new tuning modules to optimize your system.
"""

import json
import os
from src.defense.whitelist import WhitelistManager
from src.defense.threshold_optimizer import ThresholdOptimizer
from src.config.detection_config import (
    DETECTION_CONFIG,
    CONFIG_AGGRESSIVE,
    CONFIG_BALANCED,
    CONFIG_CONSERVATIVE
)


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_whitelist():
    """Demonstrate whitelist functionality."""
    print_header("1. WHITELIST MANAGER DEMO")
    
    whitelist = WhitelistManager()
    
    print("Current Trusted Domains:")
    for domain in whitelist.get_trusted_domains():
        print(f"  [OK] {domain}")
    
    print("\nCurrent Trusted Senders:")
    for sender in whitelist.get_trusted_senders():
        print(f"  [OK] {sender}")
    
    # Test emails
    test_cases = [
        ("hr@enron.com", "Should be trusted (in trusted_senders)"),
        ("ceo@enron.com", "Should be trusted (in trusted_senders)"),
        ("user@partner.com", "Should be trusted (partner.com is trusted)"),
        ("attacker@suspicious.com", "Should NOT be trusted"),
    ]
    
    print("\nWhitelist Testing:")
    for email, description in test_cases:
        status = "[TRUSTED]" if whitelist.is_whitelisted(email) else "[NOT TRUSTED]"
        print(f"  {email:<30} {status:<20} ({description})")
    
    # Demo: Add a new trusted sender
    print("\n--- Demo: Adding new trusted sender ---")
    whitelist.add_trusted_sender("finance@enron.com")
    print(f"Added: finance@enron.com")
    print(f"Is now trusted? {whitelist.is_trusted_sender('finance@enron.com')}")
    print()


def demo_thresholds():
    """Demonstrate threshold configurations."""
    print_header("2. THRESHOLD CONFIGURATIONS COMPARISON")
    
    configs = {
        "Aggressive": CONFIG_AGGRESSIVE,
        "Balanced": CONFIG_BALANCED,
        "Conservative": CONFIG_CONSERVATIVE,
    }
    
    print("Comparing key parameters across configurations:\n")
    print(f"{'Parameter':<35} {'Aggressive':<15} {'Balanced':<15} {'Conservative':<15}")
    print("-" * 80)
    
    # Compare heuristic thresholds
    print("HEURISTIC THRESHOLDS:")
    for config_name, config in configs.items():
        threshold = config['heuristic']['high_risk_threshold']
        print(f"  High Risk Threshold           {threshold:<15}", end="")
        if config_name == "Aggressive":
            configs_list = list(configs.values())
            agg, bal, con = configs_list[0]['heuristic']['high_risk_threshold'], \
                           configs_list[1]['heuristic']['high_risk_threshold'], \
                           configs_list[2]['heuristic']['high_risk_threshold']
            print(f"  {agg:<15} {bal:<15} {con:<15}")
            break
    
    print("\nURGENCY KEYWORD WEIGHT:")
    agg_urg = CONFIG_AGGRESSIVE['heuristic']['urgency_weight']
    bal_urg = CONFIG_BALANCED['heuristic']['urgency_weight']
    con_urg = CONFIG_CONSERVATIVE['heuristic']['urgency_weight']
    print(f"  Weight per hit               {agg_urg:<15} {bal_urg:<15} {con_urg:<15}")
    
    print("\nCOMBINED DETECTION WEIGHTS:")
    print(f"  Heuristic Weight             {CONFIG_AGGRESSIVE['combined']['heuristic_weight']:<15} "
          f"{CONFIG_BALANCED['combined']['heuristic_weight']:<15} "
          f"{CONFIG_CONSERVATIVE['combined']['heuristic_weight']:<15}")
    print(f"  LLM Weight                   {CONFIG_AGGRESSIVE['combined']['llm_weight']:<15} "
          f"{CONFIG_BALANCED['combined']['llm_weight']:<15} "
          f"{CONFIG_CONSERVATIVE['combined']['llm_weight']:<15}")
    
    print("\n[KEY] Key Insight:")
    print("  • Aggressive: Higher urgency weight (more sensitive) → More alerts, more false positives")
    print("  • Balanced: Medium weights → Good balance")
    print("  • Conservative: Lower weights → Fewer false positives, may miss some attacks")


def demo_optimizer():
    """Demonstrate threshold optimizer."""
    print_header("3. THRESHOLD OPTIMIZER DEMO")
    
    # Simulate test data
    print("Simulating detection results for 100 emails...\n")
    
    # Create synthetic ground truth (50 legitimate, 50 phishing)
    ground_truth = [0] * 50 + [1] * 50
    
    # Simulate predictions from different strategies
    # Aggressive: Catches 95% of phishing, but 30% false positives
    predictions_aggressive = [
        1 if (g == 1 and random.random() < 0.95)
        else (1 if g == 0 and random.random() < 0.30 else 0)
        for g in ground_truth
    ]
    
    # Balanced: Catches 85% of phishing, 10% false positives
    predictions_balanced = [
        1 if (g == 1 and random.random() < 0.85)
        else (1 if g == 0 and random.random() < 0.10 else 0)
        for g in ground_truth
    ]
    
    # Conservative: Catches 75% of phishing, 5% false positives
    predictions_conservative = [
        1 if (g == 1 and random.random() < 0.75)
        else (1 if g == 0 and random.random() < 0.05 else 0)
        for g in ground_truth
    ]
    
    optimizer = ThresholdOptimizer()
    optimizer.evaluate_config(predictions_aggressive, ground_truth, "Aggressive")
    optimizer.evaluate_config(predictions_balanced, ground_truth, "Balanced")
    optimizer.evaluate_config(predictions_conservative, ground_truth, "Conservative")
    
    # Print detailed comparison
    optimizer.compare_configs()
    
    # Show summary
    print("\nSUMMARY STATISTICS:")
    summary = optimizer.get_summary_stats()
    if summary:
        print(f"  Average F1 Score:     {summary['average_f1']:.4f}")
        print(f"  Average FPR:          {summary['average_fpr']:.4f}")
        print(f"  Average Recall:       {summary['average_recall']:.4f}")
        
        best_f1_name, best_f1 = optimizer.get_best_balanced_config()
        print(f"\n  [BEST] Recommended Config (Best F1): {best_f1_name}")


def print_quick_tips():
    """Print practical tips for tuning."""
    print_header("4. QUICK TUNING TIPS")
    
    tips = [
        ("Reduce Keyword Weights", 
         "If seeing many false positives from legitimate urgent emails:\n"
         "  → Reduce urgency_weight from 10 to 5-7\n"
         "  → Reduce authority_weight from 5 to 3"),
        
        ("Add Trusted Senders",
         "If certain users/departments always send safe emails:\n"
         "  → Add them to trusted_senders in detection_config.py\n"
         "  → Their emails get whitelist score reduction"),
        
        ("Adjust High Risk Threshold",
         "If too many alerts (false positives):\n"
         "  → Increase high_risk_threshold from 70 to 80\n"
         "  → This requires higher scores to trigger 'Alert' classification"),
        
        ("Boost LLM Confidence Filtering",
         "If LLM is making uncertain predictions:\n"
         "  → Increase confidence_min from 0.6 to 0.7\n"
         "  → Only accept high-confidence LLM predictions"),
        
        ("Use Ensemble Weighting",
         "To prioritize different detection methods:\n"
         "  → If you trust LLM more: increase llm_weight to 0.6+\n"
         "  → If heuristics are reliable: increase heuristic_weight"),
    ]
    
    for title, description in tips:
        print(f"\n[TIP] {title}")
        print(f"     {description}")


def print_files_created():
    """List the files created for tuning."""
    print_header("5. NEW FILES CREATED")
    
    files = [
        ("src/config/detection_config.py", 
         "Main configuration file with adjustable thresholds"),
        ("src/defense/whitelist.py",
         "Whitelist manager for trusted senders/domains"),
        ("src/defense/threshold_optimizer.py",
         "A/B testing tool to compare configurations"),
        ("TUNING_GUIDE.md",
         "Comprehensive guide with code examples"),
        ("test_tuning_example.py",
         "This file - demonstrates the tuning process"),
    ]
    
    print("New/Modified Files:\n")
    for filepath, description in files:
        print(f"  [OK] {filepath:<40} - {description}")
    
    print("\n\nNext Steps:")
    print("  1. Update src/defense/heuristic_analyzer.py to use DETECTION_CONFIG")
    print("  2. Update src/defense/llm_classifier.py to use confidence filtering")
    print("  3. Run tests with different configurations")
    print("  4. Use ThresholdOptimizer to find the best balance")
    print("  5. Deploy the best configuration to production")


import random


def main():
    """Run all demonstrations."""
    print("\n")
    print("=" * 70)
    print("  PHISHING DETECTION SYSTEM - TUNING & OPTIMIZATION GUIDE".center(70))
    print("=" * 70)
    
    try:
        demo_whitelist()
        demo_thresholds()
        demo_optimizer()
        print_quick_tips()
        print_files_created()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] Demo Complete! Review TUNING_GUIDE.md for detailed instructions.")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\nERROR during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
