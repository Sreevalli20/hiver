#!/usr/bin/env python3
"""
Generate failure analysis from real evaluation results.
"""

import pandas as pd
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.classifier import IntentClassifier
from app.retrieval import RetrievalSystem
from app.escalation import EscalationPolicy

def load_golden_set():
    """Load golden set."""
    golden_file = Path("golden/golden_200.csv")
    golden_df = pd.read_csv(golden_file)
    golden_df = golden_df.dropna(subset=['message'])
    return golden_df

def load_models():
    """Load trained models."""
    classifier = IntentClassifier("models")
    retrieval = RetrievalSystem()
    retrieval.load("models")
    escalation = EscalationPolicy()
    return classifier, retrieval, escalation

def analyze_failures(golden_df, classifier, retrieval, escalation):
    """Analyze failures from real evaluation."""
    
    print("Analyzing failures...")
    
    failures = []
    
    for idx, row in golden_df.iterrows():
        message = row['message']
        true_intent = row['intent']
        true_action = row['expected_action']
        
        # Predict
        pred = classifier.predict(message)
        pred_intent = pred['intent']
        confidence = pred['confidence']
        
        # Retrieve evidence
        evidence = retrieval.retrieve(message, k=5)
        
        # Escalation decision
        decision = escalation.decide(pred_intent, confidence, evidence)
        pred_action = decision['decision']
        
        # Check for failures
        if pred_intent != true_intent:
            failures.append({
                'type': 'intent_misclassification',
                'input': message,
                'predicted_intent': pred_intent,
                'expected_intent': true_intent,
                'confidence': confidence,
                'decision': pred_action,
                'expected_action': true_action,
                'explanation': f"Classifier predicted {pred_intent} instead of {true_intent}"
            })
        
        if pred_action != true_action:
            failures.append({
                'type': 'escalation_mismatch',
                'input': message,
                'predicted_intent': pred_intent,
                'expected_intent': true_intent,
                'confidence': confidence,
                'decision': pred_action,
                'expected_action': true_action,
                'explanation': f"System decided {pred_action} instead of {true_action}"
            })
    
    print(f"Found {len(failures)} failures")
    
    return failures

def identify_top_failure_modes(failures):
    """Identify top 5 failure modes."""
    
    # Group by type
    intent_failures = [f for f in failures if f['type'] == 'intent_misclassification']
    escalation_failures = [f for f in failures if f['type'] == 'escalation_mismatch']
    
    # Analyze intent misclassifications
    intent_confusion = {}
    for f in intent_failures:
        key = (f['expected_intent'], f['predicted_intent'])
        intent_confusion[key] = intent_confusion.get(key, 0) + 1
    
    # Analyze escalation mismatches
    escalation_patterns = {}
    for f in escalation_failures:
        key = (f['expected_action'], f['decision'])
        escalation_patterns[key] = escalation_patterns.get(key, 0) + 1
    
    # Select top 5 failure modes
    top_failures = []
    
    # Add top intent confusions
    for (expected, predicted), count in sorted(intent_confusion.items(), key=lambda x: x[1], reverse=True)[:3]:
        example = next(f for f in intent_failures if f['expected_intent'] == expected and f['predicted_intent'] == predicted)
        top_failures.append({
            'mode': f"Intent Confusion: {expected} -> {predicted}",
            'count': count,
            'example': example
        })
    
    # Add top escalation mismatches
    for (expected, predicted), count in sorted(escalation_patterns.items(), key=lambda x: x[1], reverse=True)[:2]:
        example = next(f for f in escalation_failures if f['expected_action'] == expected and f['decision'] == predicted)
        top_failures.append({
            'mode': f"Escalation Mismatch: {expected} -> {predicted}",
            'count': count,
            'example': example
        })
    
    return top_failures

def generate_failure_report(top_failures):
    """Generate detailed failure report."""
    
    report = []
    report.append("# Failure Analysis from Real Evaluation\n")
    report.append("This analysis is based on real Twitter customer support data from AmazonHelp.\n")
    
    for i, failure in enumerate(top_failures[:5], 1):
        report.append(f"## Failure Mode {i}: {failure['mode']}")
        report.append(f"**Frequency:** {failure['count']} occurrences\n")
        
        ex = failure['example']
        report.append(f"**Real Input:** {ex['input'][:200]}...")
        report.append(f"**Predicted Intent:** {ex['predicted_intent']}")
        report.append(f"**Expected Intent:** {ex['expected_intent']}")
        report.append(f"**Decision:** {ex['decision']}")
        report.append(f"**Expected Action:** {ex['expected_action']}")
        report.append(f"**Confidence:** {ex['confidence']:.2f}")
        report.append(f"**Explanation:** {ex['explanation']}")
        
        # Generate hypothesis
        if 'Intent Confusion' in failure['mode']:
            report.append("**Hypothesis:** Similar vocabulary or semantic overlap between intents causes confusion.")
            report.append("**Proposed Improvement:** Add intent-specific discriminative features or use semantic embeddings.")
        elif 'Escalation Mismatch' in failure['mode']:
            if ex['decision'] == 'AUTO_HANDLE' and ex['expected_action'] == 'ESCALATE':
                report.append("**Hypothesis:** Escalation policy may be too aggressive in auto-handling complex cases.")
                report.append("**Proposed Improvement:** Add complexity-based escalation triggers or lower confidence threshold.")
            else:
                report.append("**Hypothesis:** Escalation policy may be too conservative.")
                report.append("**Proposed Improvement:** Adjust confidence thresholds or add evidence quality checks.")
        
        report.append("\n" + "-"*80 + "\n")
    
    return "\n".join(report)

def main():
    """Main analysis function."""
    
    # Load data
    golden_df = load_golden_set()
    print(f"Loaded {len(golden_df)} golden examples")
    
    # Load models
    classifier, retrieval, escalation = load_models()
    print("Models loaded")
    
    # Analyze failures
    failures = analyze_failures(golden_df, classifier, retrieval, escalation)
    
    # Identify top failure modes
    top_failures = identify_top_failure_modes(failures)
    
    # Generate report
    report = generate_failure_report(top_failures)
    
    # Save report
    output_file = Path("docs/failure_analysis.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\nFailure analysis saved to {output_file}")
    
    # Also save raw failures for reference
    failures_file = Path("evaluation/results/failures.json")
    failures_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(failures_file, 'w') as f:
        json.dump(failures, f, indent=2)
    
    print(f"Raw failures saved to {failures_file}")

if __name__ == "__main__":
    main()
