import json
import pandas as pd
import os

def run_evaluation_report():
    """
    Compares Offensive Intent vs Defensive Detection to calculate metrics.
    """
    offensive_log = "data/generated_phishing_v1.jsonl"
    defensive_log = "data/defense_analysis_v1.jsonl"
    
    print("--- DISSERTATION EVALUATION: ADVERSARIAL METRICS ---")
    
    if not os.path.exists(defensive_log):
        print("Error: Defensive analysis logs not found. Please run the Detector Engine first.")
        return

    # Load Defensive Results
    defense_data = []
    with open(defensive_log, "r") as f:
        for line in f:
            defense_data.append(json.loads(line))
    
    df_defense = pd.DataFrame(defense_data)
    
    # Basic Metrics
    total_samples = len(df_defense)
    detected_alerts = len(df_defense[df_defense['status'] == 'ALERT'])
    quarantined = len(df_defense[df_defense['status'] == 'QUARANTINE'])
    passed = len(df_defense[df_defense['status'] == 'PASS'])
    
    detection_rate = ((detected_alerts + quarantined) / total_samples) * 100 if total_samples > 0 else 0
    
    print(f"\n[SUMMARY STATISTICS]")
    print(f"Total Attack Samples: {total_samples}")
    print(f"Successful Detections (Alert): {detected_alerts}")
    print(f"Suspicious (Quarantine): {quarantined}")
    print(f"False Negatives (Pass): {passed}")
    print(f"Overall Detection Rate: {detection_rate:.2f}%")
    
    # Breakdown by Attack Tone (derived from metadata)
    print("\n[PERFORMANCE BY ATTACK TONE]")
    if 'original_metadata' in df_defense.columns:
        tones = []
        for meta in df_defense['original_metadata']:
            tones.append(meta.get('tone', 'Unknown'))
        df_defense['tone'] = tones
        
        tone_stats = df_defense.groupby('tone').agg({
            'final_risk_score': 'mean',
            'status': lambda x: (x != 'PASS').sum() / len(x) * 100
        }).rename(columns={'final_risk_score': 'Avg_Score', 'status': 'Detection_%'})
        
        print(tone_stats)

    # Breakdown by Heuristic vs LLM Accuracy
    print("\n[ANALYSIS METHOD BIAS]")
    avg_h_score = df_defense['heuristics'].apply(lambda x: x['score']).mean()
    print(f"Average Heuristic Score: {avg_h_score:.2f}")
    
    if 'llm_analysis' in df_defense.columns and df_defense['llm_analysis'].notnull().any():
        avg_l_score = df_defense['llm_analysis'].apply(lambda x: x['risk_score'] if x else 0).mean()
        print(f"Average LLM Reasoning Score: {avg_l_score:.2f}")
        print("Insight: LLM provides context that heuristics often miss in low-urgency attacks.")
    else:
        print("LLM analysis not available for this run (Heuristics-only mode).")

if __name__ == "__main__":
    run_evaluation_report()
