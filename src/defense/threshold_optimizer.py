"""
Threshold Optimizer Module
Tests different threshold configurations to find optimal balance between 
detection accuracy and false positive rate.
"""

import json


# Manual implementation of metrics to avoid sklearn dependency
def accuracy_score(y_true, y_pred):
    """Calculate accuracy without sklearn."""
    if len(y_true) == 0:
        return 0
    return sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp) / len(y_true)


def confusion_matrix(y_true, y_pred, labels=None):
    """Calculate confusion matrix without sklearn."""
    if labels is None:
        labels = [0, 1]
    
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    
    return [[tn, fp], [fn, tp]]


def precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0):
    """Calculate precision, recall, f1, support without sklearn."""
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else zero_division
    recall = tp / (tp + fn) if (tp + fn) > 0 else zero_division
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else zero_division
    support = sum(1 for yt in y_true if yt == 1)
    
    return precision, recall, f1, support


def roc_auc_score(y_true, y_score):
    """Calculate ROC AUC without sklearn."""
    # Simple implementation for binary classification
    try:
        sorted_scores = sorted(zip(y_true, y_score), key=lambda x: x[1], reverse=True)
        n_pos = sum(1 for yt in y_true if yt == 1)
        n_neg = sum(1 for yt in y_true if yt == 0)
        
        if n_pos == 0 or n_neg == 0:
            return 0.5
        
        tp = 0
        fp = 0
        auc = 0
        prev_score = None
        
        for y, score in sorted_scores:
            if prev_score is not None and score != prev_score:
                auc += tp * fp
                prev_score = score
            
            if y == 1:
                tp += 1
            else:
                fp += 1
        
        auc += tp * fp
        return auc / (n_pos * n_neg) if (n_pos * n_neg) > 0 else 0.5
    except:
        return 0.5


class ThresholdOptimizer:
    """
    Evaluates different detection configurations against ground truth data.
    
    Usage:
        optimizer = ThresholdOptimizer()
        results = optimizer.evaluate_config(predictions, ground_truth, "Config_v1")
        optimizer.compare_configs()
    """
    
    def __init__(self):
        """Initialize the optimizer with empty results dictionary."""
        self.results = {}
        self.ground_truth_data = None
    
    def evaluate_config(self, predictions, ground_truth, config_name):
        """
        Evaluate a single configuration against ground truth.
        
        Args:
            predictions: List of predicted labels (0=Safe, 1=Phishing)
            ground_truth: List of actual labels (0=Safe, 1=Phishing)
            config_name: Name of the configuration being tested
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Ensure both lists are same length
        assert len(predictions) == len(ground_truth), \
            f"Length mismatch: {len(predictions)} predictions vs {len(ground_truth)} labels"
        
        # Calculate basic metrics
        accuracy = accuracy_score(ground_truth, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, average='binary', zero_division=0
        )
        
        # Calculate confusion matrix
        cm = confusion_matrix(ground_truth, predictions, labels=[0, 1])
        tn, fp = cm[0][0], cm[0][1]
        fn, tp = cm[1][0], cm[1][1]
        
        # Calculate rates
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # True Positive Rate (Recall)
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate
        
        # Try to calculate AUC if predictions are probabilities
        auc_score = None
        try:
            if all(isinstance(p, (int, float)) and 0 <= p <= 1 for p in predictions):
                auc_score = roc_auc_score(ground_truth, predictions)
        except:
            pass
        
        # Store results
        metrics = {
            "config_name": config_name,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "true_positive_rate": round(tpr, 4),
            "false_positive_rate": round(fpr, 4),
            "specificity": round(specificity, 4),
            "auc_score": round(auc_score, 4) if auc_score else None,
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "total_samples": len(ground_truth),
        }
        
        self.results[config_name] = metrics
        return metrics
    
    def get_best_config(self, metric="f1_score"):
        """
        Get the configuration with the best score for a specific metric.
        
        Args:
            metric: Metric to use for comparison 
                   (default: "f1_score")
        
        Returns:
            Tuple of (config_name, metrics_dict)
        """
        if not self.results:
            return None, None
        
        best_config = max(
            self.results.items(),
            key=lambda x: x[1].get(metric, 0)
        )
        return best_config
    
    def get_best_balanced_config(self):
        """
        Get configuration with best balance between precision and recall.
        Uses F1 score as the metric (harmonic mean of precision and recall).
        
        Returns:
            Tuple of (config_name, metrics_dict)
        """
        return self.get_best_config(metric="f1_score")
    
    def get_config_with_lowest_fpr(self):
        """
        Get configuration with lowest false positive rate.
        Useful when you want to minimize user frustration from false alarms.
        
        Returns:
            Tuple of (config_name, metrics_dict)
        """
        if not self.results:
            return None, None
        
        best_config = min(
            self.results.items(),
            key=lambda x: x[1].get("false_positive_rate", 1)
        )
        return best_config
    
    def compare_configs(self, save_to_file=None):
        """
        Print detailed comparison of all tested configurations.
        
        Args:
            save_to_file: Optional filepath to save results as JSON
        """
        if not self.results:
            print("No results to compare. Run evaluate_config() first.")
            return
        
        output = "\n" + "="*100 + "\n"
        output += "THRESHOLD OPTIMIZATION RESULTS COMPARISON\n"
        output += "="*100 + "\n\n"
        
        # Table header
        output += f"{'Config':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'FPR':<12}\n"
        output += "-"*80 + "\n"
        
        # Data rows
        for config_name, metrics in self.results.items():
            output += f"{config_name:<20} "
            output += f"{metrics['accuracy']:<12.4f} "
            output += f"{metrics['precision']:<12.4f} "
            output += f"{metrics['recall']:<12.4f} "
            output += f"{metrics['f1_score']:<12.4f} "
            output += f"{metrics['false_positive_rate']:<12.4f}\n"
        
        output += "\n" + "="*100 + "\n"
        output += "DETAILED BREAKDOWN\n"
        output += "="*100 + "\n\n"
        
        # Detailed breakdown for each config
        for config_name, metrics in self.results.items():
            output += f"\n📊 Configuration: {config_name}\n"
            output += "-" * 50 + "\n"
            output += f"  Accuracy:              {metrics['accuracy']:.1%}\n"
            output += f"  Precision:             {metrics['precision']:.1%}\n"
            output += f"  Recall (Sensitivity):  {metrics['recall']:.1%}\n"
            output += f"  F1 Score:              {metrics['f1_score']:.1%}\n"
            output += f"  Specificity:           {metrics['specificity']:.1%}\n"
            output += f"  True Positive Rate:    {metrics['true_positive_rate']:.1%}\n"
            output += f"  False Positive Rate:   {metrics['false_positive_rate']:.1%}\n"
            if metrics['auc_score']:
                output += f"  AUC Score:             {metrics['auc_score']:.4f}\n"
            output += f"\n  Confusion Matrix:\n"
            output += f"    True Negatives:  {metrics['true_negatives']:<6} (Legitimate emails correctly passed)\n"
            output += f"    True Positives:  {metrics['true_positives']:<6} (Phishing emails correctly detected)\n"
            output += f"    False Positives: {metrics['false_positives']:<6} (Legitimate emails incorrectly flagged)\n"
            output += f"    False Negatives: {metrics['false_negatives']:<6} (Phishing emails missed)\n"
        
        output += "\n" + "="*100 + "\n"
        output += "RECOMMENDATIONS\n"
        output += "="*100 + "\n\n"
        
        # Find best configs
        best_f1_name, best_f1 = self.get_best_balanced_config()
        best_fpr_name, best_fpr = self.get_config_with_lowest_fpr()
        
        output += f"✓ Best F1 Score (Balance):     {best_f1_name} (F1={best_f1['f1_score']:.4f})\n"
        output += f"✓ Best FPR (User-Friendly):    {best_fpr_name} (FPR={best_fpr['false_positive_rate']:.4f})\n"
        
        print(output)
        
        # Optionally save to file
        if save_to_file:
            with open(save_to_file, 'w') as f:
                f.write(output)
                f.write("\n\n=== RAW DATA ===\n")
                json.dump(self.results, f, indent=2)
            print(f"\n✓ Results saved to {save_to_file}")
    
    def get_summary_stats(self):
        """
        Get summary statistics across all tested configurations.
        
        Returns:
            Dictionary with aggregate statistics
        """
        if not self.results:
            return None
        
        f1_scores = [m['f1_score'] for m in self.results.values()]
        fprs = [m['false_positive_rate'] for m in self.results.values()]
        recalls = [m['recall'] for m in self.results.values()]
        
        return {
            "average_f1": round(sum(f1_scores) / len(f1_scores), 4),
            "max_f1": round(max(f1_scores), 4),
            "min_f1": round(min(f1_scores), 4),
            "average_fpr": round(sum(fprs) / len(fprs), 4),
            "max_fpr": round(max(fprs), 4),
            "min_fpr": round(min(fprs), 4),
            "average_recall": round(sum(recalls) / len(recalls), 4),
        }
    
    def export_results(self, filepath):
        """
        Export all results to a JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✓ Results exported to {filepath}")
    
    def clear_results(self):
        """Clear all stored results."""
        self.results = {}


if __name__ == "__main__":
    # Example usage
    print("Threshold Optimizer Module")
    print("=" * 50)
    
    # Simulate some test data
    import random
    random.seed(42)
    
    ground_truth = [0] * 50 + [1] * 50  # 50 legitimate, 50 phishing
    
    # Config 1: Aggressive (catches more phishing, but more false positives)
    predictions1 = [
        1 if (g == 1 or random.random() < 0.2) else 0
        for g in ground_truth
    ]
    
    # Config 2: Balanced
    predictions2 = [
        1 if (g == 1 or random.random() < 0.1) else 0
        for g in ground_truth
    ]
    
    # Config 3: Conservative (fewer false positives, fewer true positives)
    predictions3 = [
        1 if (g == 1 and random.random() < 0.85) else 0
        for g in ground_truth
    ]
    
    optimizer = ThresholdOptimizer()
    optimizer.evaluate_config(predictions1, ground_truth, "Aggressive")
    optimizer.evaluate_config(predictions2, ground_truth, "Balanced")
    optimizer.evaluate_config(predictions3, ground_truth, "Conservative")
    
    optimizer.compare_configs()
    
    print("\nSummary Stats:")
    print(json.dumps(optimizer.get_summary_stats(), indent=2))
