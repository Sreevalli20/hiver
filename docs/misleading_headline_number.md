# What is Misleading About My Headline Number?

## Class Imbalance

The intent classification dataset exhibits significant class imbalance. While the overall accuracy may appear high (e.g., 85%), this metric is inflated by the prevalence of common intents like "order_status" and "general_inquiry" which may constitute 40-50% of the data. The macro F1 score (e.g., 72%) provides a more honest picture by treating all intents equally, revealing that performance on rare intents like "escalation_required" is substantially lower.

**Concrete example:** If "order_status" represents 45% of the data and the classifier achieves 95% accuracy on this class, it contributes 42.75 percentage points to overall accuracy even if it performs poorly on other classes.

## Rare Intents

The system's performance on rare intents is disproportionately worse than headline metrics suggest. Intents like "escalation_required" and "account_issue" appear infrequently in the training data (often <5% combined), leading to poor generalization. However, these are precisely the intents where errors are most costly—failing to escalate a legal threat or security issue has business-critical consequences.

**Concrete example:** An escalation_required intent might have precision of 60% and recall of 50%, while common intents exceed 90% on both metrics. The weighted average hides this dangerous gap.

## Accuracy vs Macro F1

The headline accuracy number is misleading because it doesn't account for the cost of different error types. A classifier that always predicts the majority class could achieve 45% accuracy but would be useless in practice. Macro F1 is more honest but still doesn't capture the asymmetric costs of false negatives in escalation decisions.

**Concrete example:** With 10 intents, random guessing yields ~10% accuracy. A classifier achieving 70% accuracy represents a 7x improvement over random, but if it fails on the 2 most critical intents, the system is not production-ready.

## Escalation Risk

The escalation F1 score (e.g., 78%) is misleading because false negatives are far more dangerous than false positives. Incorrectly auto-handling a case that should escalate (false negative) could lead to legal issues, security breaches, or severe customer dissatisfaction. However, the F1 score treats false positives and false negatives equally.

**Concrete example:** An escalation recall of 85% means 15% of cases requiring human intervention are incorrectly auto-handled. If 100 such cases occur daily, 15 critical issues are mishandled—unacceptable in production.

## Offline vs Production Performance

The evaluation metrics are based on a curated golden set of 200 examples that may not reflect real-world distribution. The golden set intentionally includes balanced representation of all intents and difficulty levels, but production traffic will be heavily skewed toward common intents and may contain noisier, more ambiguous language.

**Concrete example:** The golden set contains 20 examples of "escalation_required" (10%), but in production this intent might appear in only 0.5% of traffic. The classifier's performance on this intent in the evaluation may not generalize to actual rare occurrences.

## Golden Set Limitations

The golden evaluation set of 200 examples, while carefully curated, has several limitations:
- It was labeled by a single human evaluator, introducing potential bias
- It represents a snapshot in time and may not reflect seasonal patterns or new issue types
- The "difficulty" labels are subjective and may not align with actual model behavior
- It doesn't include multi-turn conversations or context from previous interactions

**Concrete example:** Two evaluators might disagree on whether "I need to speak to a manager" should be "escalation_required" or "complaint," affecting the ground truth for evaluation.

## LLM Judge Limitations

The LLM-as-judge evaluation, while providing a structured rubric, has inherent limitations:
- The deterministic fallback used in this implementation is rule-based and may not capture nuanced quality dimensions
- A true LLM judge would require external API credentials, making core evaluation dependent on third-party services
- Human-judge agreement rates (e.g., 65% exact agreement) indicate significant subjectivity in reply quality assessment
- The 1-5 scale has limited granularity—most responses cluster around 3-4, making discrimination difficult

**Concrete example:** A human might rate a response as 4 for helpfulness while the deterministic judge rates it 3, reflecting the subjective nature of quality assessment.

## Summary

The headline numbers (accuracy, F1, quality scores) are useful for comparing systems but should not be interpreted as absolute measures of production readiness. The most honest assessment considers:
- Macro F1 rather than accuracy for intent classification
- Escalation recall as the critical metric for safety
- Performance on rare, high-stakes intents
- The gap between offline evaluation and real-world performance
- The limitations of both the golden set and evaluation methodology

**Key takeaway:** A system with 85% intent accuracy and 78% escalation F1 may still fail catastrophically on the 0.5% of cases that require human intervention, which is why the escalation policy defaults to escalation when uncertain.
