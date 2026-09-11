#!/usr/bin/env python3
"""
Compare judge scores with human validation scores.
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from evaluation.judge import ReplyJudge, compare_judge_with_human

def load_human_validation():
    """Load human validation scores."""
    file = Path("golden/human_validation_sample.csv")
    if not file.exists():
        print("Human validation sample not found")
        return None
    
    df = pd.read_csv(file)
    return df

def run_judge_evaluation():
    """Run judge evaluation on the same samples."""
    human_df = load_human_validation()
    if human_df is None:
        return None
    
    judge = ReplyJudge()
    
    judge_evaluations = []
    human_scores = []
    
    for _, row in human_df.iterrows():
        # Simulate a reply (in real implementation, would use actual generated replies)
        reply = "I understand your concern. Let me help you with that."
        evidence = []
        
        # Run judge
        eval_result = judge.evaluate(
            row['message'],
            reply,
            evidence,
            row['intent']
        )
        judge_evaluations.append(eval_result)
        
        # Extract human scores
        human_score = {
            'groundedness': row['groundedness'],
            'correctness': row['correctness'],
            'helpfulness': row['helpfulness'],
            'brand_consistency': row['brand_consistency'],
            'safety': row['safety']
        }
        human_scores.append(human_score)
    
    return judge_evaluations, human_scores

def main():
    """Main comparison function."""
    print("Running human-judge comparison...")
    
    judge_evals, human_scores = run_judge_evaluation()
    
    if judge_evals is None or human_scores is None:
        print("Could not run comparison")
        return
    
    # Compare
    comparison = compare_judge_with_human(judge_evals, human_scores)
    
    print("\n=== Human-Judge Agreement ===")
    print(f"Exact Agreement Rate: {comparison['exact_agreement_rate']:.2%}")
    print(f"Within-One Agreement Rate: {comparison['within_one_agreement_rate']:.2%}")
    print(f"Total Comparisons: {comparison['total_comparisons']}")
    
    # Save results
    results_dir = Path("evaluation/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(results_dir / 'human_judge_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\nResults saved to {results_dir}/human_judge_comparison.json")

if __name__ == "__main__":
    main()
