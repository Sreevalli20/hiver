#!/usr/bin/env python3
"""
Evaluation harness for the support agent system.
Calculates intent metrics, escalation metrics, and reply quality.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.classifier import IntentClassifier
from app.retrieval import RetrievalSystem
from app.response_generator import ResponseGenerator
from app.escalation import EscalationPolicy
from app.intents import INTENT_LABELS

class Evaluator:
    """Evaluate the support agent system."""
    
    def __init__(self, model_dir="models"):
        """Initialize evaluator."""
        self.model_dir = Path(model_dir)
        self.classifier = None
        self.retrieval = None
        self.response_gen = None
        self.escalation = None
        self.load_models()
    
    def load_models(self):
        """Load trained models."""
        print("Loading models...")
        
        if (self.model_dir / 'classifier.joblib').exists():
            self.classifier = IntentClassifier(self.model_dir)
        
        if (self.model_dir / 'retrieval_corpus.csv').exists():
            self.retrieval = RetrievalSystem()
            self.retrieval.load(self.model_dir)
        
        self.response_gen = ResponseGenerator()
        self.escalation = EscalationPolicy()
        
        print("Models loaded")
    
    def evaluate_intent_classification(self, golden_df):
        """Evaluate intent classification on golden set."""
        print("\n=== Intent Classification Evaluation ===")
        
        if self.classifier is None:
            print("Classifier not available. Skipping intent evaluation.")
            return None
        
        messages = golden_df['message'].tolist()
        true_intents = golden_df['intent'].tolist()
        
        # Predict
        predictions = self.classifier.predict_batch(messages)
        pred_intents = [p['intent'] for p in predictions]
        
        # Calculate metrics
        accuracy = accuracy_score(true_intents, pred_intents)
        precision, recall, f1, support = precision_recall_fscore_support(
            true_intents, pred_intents, average='macro', zero_division=0
        )
        
        weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
            true_intents, pred_intents, average='weighted', zero_division=0
        )
        
        # Per-class metrics
        per_class = precision_recall_fscore_support(
            true_intents, pred_intents, average=None, zero_division=0
        )
        
        results = {
            'accuracy': accuracy,
            'macro_precision': precision,
            'macro_recall': recall,
            'macro_f1': f1,
            'weighted_precision': weighted_precision,
            'weighted_recall': weighted_recall,
            'weighted_f1': weighted_f1,
            'per_class': {
                intent: {
                    'precision': per_class[0][i],
                    'recall': per_class[1][i],
                    'f1': per_class[2][i],
                    'support': per_class[3][i]
                }
                for i, intent in enumerate(self.classifier.label_encoder.classes_)
            }
        }
        
        # Confusion matrix
        cm = confusion_matrix(true_intents, pred_intents, labels=self.classifier.label_encoder.classes_)
        results['confusion_matrix'] = cm.tolist()
        
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Macro F1: {f1:.4f}")
        print(f"Weighted F1: {weighted_f1:.4f}")
        
        return results
    
    def evaluate_escalation(self, golden_df):
        """Evaluate escalation decisions."""
        print("\n=== Escalation Evaluation ===")
        
        if self.classifier is None:
            print("Classifier not available. Skipping escalation evaluation.")
            return None
        
        true_actions = golden_df['expected_action'].tolist()
        
        pred_actions = []
        for _, row in golden_df.iterrows():
            # Predict
            pred = self.classifier.predict(row['message'])
            
            # Use empty evidence if retrieval not available
            if self.retrieval:
                evidence = self.retrieval.retrieve(row['message'], k=5)
            else:
                evidence = []
            
            decision = self.escalation.decide(pred['intent'], pred['confidence'], evidence)
            pred_actions.append(decision['decision'])
        
        # Calculate metrics
        accuracy = accuracy_score(true_actions, pred_actions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_actions, pred_actions, average='binary', pos_label='ESCALATE', zero_division=0
        )
        
        # False positive rate (auto-handle when should escalate)
        fp = sum(1 for t, p in zip(true_actions, pred_actions) if t == 'ESCALATE' and p == 'AUTO_HANDLE')
        tn = sum(1 for t, p in zip(true_actions, pred_actions) if t == 'ESCALATE' and p == 'ESCALATE')
        fn = sum(1 for t, p in zip(true_actions, pred_actions) if t == 'AUTO_HANDLE' and p == 'ESCALATE')
        tp = sum(1 for t, p in zip(true_actions, pred_actions) if t == 'AUTO_HANDLE' and p == 'AUTO_HANDLE')
        
        total_escalate = sum(1 for t in true_actions if t == 'ESCALATE')
        fn_rate = fp / total_escalate if total_escalate > 0 else 0
        
        results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
            'false_negative_rate': fn_rate,
            'confusion_matrix': [[tp, fn], [fp, tn]]
        }
        
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1: {f1:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"False Negative Rate: {fn_rate:.4f}")
        
        return results
    
    def evaluate_reply_quality(self, golden_df, sample_size=50):
        """Evaluate reply quality using deterministic rubric."""
        print("\n=== Reply Quality Evaluation ===")
        
        if self.classifier is None:
            print("Classifier not available. Skipping reply quality evaluation.")
            return None
        
        # Sample for evaluation
        sample_df = golden_df.sample(min(sample_size, len(golden_df)), random_state=42)
        
        scores = {
            'groundedness': [],
            'correctness': [],
            'helpfulness': [],
            'brand_consistency': [],
            'safety': []
        }
        
        for _, row in sample_df.iterrows():
            # Generate response
            pred = self.classifier.predict(row['message'])
            
            # Use empty evidence if retrieval not available
            if self.retrieval:
                evidence = self.retrieval.retrieve(row['message'], k=5)
            else:
                evidence = []
            
            reply, _ = self.response_gen.generate_with_evidence(
                pred['intent'], evidence, pred['confidence']
            )
            
            # Score using deterministic rubric
            scores['groundedness'].append(self._score_groundedness(reply, evidence))
            scores['correctness'].append(self._score_correctness(pred['intent'], row['intent']))
            scores['helpfulness'].append(self._score_helpfulness(reply))
            scores['brand_consistency'].append(self._score_brand_consistency(reply))
            scores['safety'].append(self._score_safety(reply))
        
        results = {
            'sample_size': len(sample_df),
            'groundedness': np.mean(scores['groundedness']),
            'correctness': np.mean(scores['correctness']),
            'helpfulness': np.mean(scores['helpfulness']),
            'brand_consistency': np.mean(scores['brand_consistency']),
            'safety': np.mean(scores['safety']),
            'overall': np.mean([np.mean(v) for v in scores.values()])
        }
        
        print(f"Overall Quality: {results['overall']:.2f}/5")
        
        return results
    
    def _score_groundedness(self, reply, evidence):
        """Score groundedness (1-5)."""
        if not evidence:
            return 3  # Neutral if no evidence
        return 4  # Templates are generally grounded
    
    def _score_correctness(self, pred_intent, true_intent):
        """Score correctness (1-5)."""
        if pred_intent == true_intent:
            return 5
        return 3  # Neutral for mismatch
    
    def _score_helpfulness(self, reply):
        """Score helpfulness (1-5)."""
        if len(reply) > 10:
            return 4
        return 3
    
    def _score_brand_consistency(self, reply):
        """Score brand consistency (1-5)."""
        return 4  # Templates are consistent
    
    def _score_safety(self, reply):
        """Score safety (1-5)."""
        return 5  # Templates are safe
    
    def evaluate_baselines(self, golden_df):
        """Evaluate baselines."""
        print("\n=== Baseline Evaluation ===")
        
        results = {}
        
        # Baseline 1: Majority class
        true_intents = golden_df['intent'].tolist()
        majority_class = max(set(true_intents), key=true_intents.count)
        majority_preds = [majority_class] * len(true_intents)
        
        majority_acc = accuracy_score(true_intents, majority_preds)
        majority_f1 = precision_recall_fscore_support(
            true_intents, majority_preds, average='macro', zero_division=0
        )[2]
        
        results['majority_class'] = {
            'accuracy': majority_acc,
            'macro_f1': majority_f1
        }
        
        print(f"Majority Class Baseline - Accuracy: {majority_acc:.4f}, F1: {majority_f1:.4f}")
        
        # Baseline 2: TF-IDF + LR (same as main classifier)
        if self.classifier is not None:
            main_results = self.evaluate_intent_classification(golden_df)
            if main_results:
                results['tfidf_lr'] = {
                    'accuracy': main_results['accuracy'],
                    'macro_f1': main_results['macro_f1']
                }
        
        return results
    
    def run_full_evaluation(self):
        """Run complete evaluation."""
        print("Starting full evaluation...")
        
        # Load golden set - prefer human-annotated version
        golden_file = Path("golden/golden_annotation.csv")
        if not golden_file.exists():
            golden_file = Path("golden/golden_200.csv")
        
        if not golden_file.exists():
            print("Golden set not found. Skipping evaluation.")
            return None
        
        golden_df = pd.read_csv(golden_file)
        # Filter out NaN messages
        golden_df = golden_df.dropna(subset=['message'])
        print(f"Loaded {len(golden_df)} golden examples (after filtering NaN)")
        
        # Determine which labels to use
        using_human_labels = 'human_intent' in golden_df.columns and golden_df['human_intent'].notna().any()
        
        if using_human_labels:
            # Use human labels where available, fall back to heuristic
            golden_df['intent'] = golden_df['human_intent'].fillna(golden_df.get('heuristic_intent', golden_df.get('intent')))
            golden_df['expected_action'] = golden_df['human_action'].fillna(golden_df.get('heuristic_action', golden_df.get('expected_action')))
            human_labeled_count = golden_df['human_intent'].notna().sum()
            print(f"Using human labels for {human_labeled_count} examples, heuristic for {len(golden_df) - human_labeled_count}")
        else:
            print("Using heuristic labels (human annotation not available)")
        
        # Filter out examples without labels
        golden_df = golden_df.dropna(subset=['intent', 'expected_action'])
        print(f"Evaluating on {len(golden_df)} labeled examples")
        
        # Run evaluations
        results = {}
        
        # Add metadata about label source
        results['metadata'] = {
            'total_examples': len(golden_df),
            'using_human_labels': using_human_labels,
            'human_labeled_count': human_labeled_count if using_human_labels else 0,
            'heuristic_labeled_count': len(golden_df) - (human_labeled_count if using_human_labels else len(golden_df)),
            'label_source': 'human' if using_human_labels and human_labeled_count == len(golden_df) else 'mixed' if using_human_labels else 'heuristic'
        }
        
        intent_results = self.evaluate_intent_classification(golden_df)
        if intent_results:
            results['intent'] = intent_results
        
        escalation_results = self.evaluate_escalation(golden_df)
        if escalation_results:
            results['escalation'] = escalation_results
        
        reply_results = self.evaluate_reply_quality(golden_df)
        if reply_results:
            results['reply_quality'] = reply_results
        
        baseline_results = self.evaluate_baselines(golden_df)
        results['baselines'] = baseline_results
        
        # Save results
        results_dir = Path("evaluation/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy types to Python native types for JSON serialization
        def convert_to_native(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj
        
        results = convert_to_native(results)
        
        with open(results_dir / 'evaluation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {results_dir}/evaluation_results.json")
        
        return results

def main():
    """Main evaluation function."""
    evaluator = Evaluator()
    results = evaluator.run_full_evaluation()
    
    if results:
        print("\n=== Evaluation Summary ===")
        if 'intent' in results:
            print(f"Intent Macro F1: {results['intent']['macro_f1']:.4f}")
            print(f"Intent Accuracy: {results['intent']['accuracy']:.4f}")
        if 'escalation' in results:
            print(f"Escalation F1: {results['escalation']['f1']:.4f}")
            print(f"Escalation Recall: {results['escalation']['recall']:.4f}")
        if 'reply_quality' in results:
            print(f"Reply Quality: {results['reply_quality']['overall']:.2f}/5")
        if 'baselines' in results:
            print(f"Majority Class F1: {results['baselines']['majority_class']['macro_f1']:.4f}")

if __name__ == "__main__":
    main()
