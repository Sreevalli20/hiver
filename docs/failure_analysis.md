# Failure Analysis from Real Evaluation

This analysis is based on real Twitter customer support data from AmazonHelp.

## Failure Mode 1: Intent Confusion: general_inquiry -> billing_issue
**Frequency:** 1 occurrences

**Real Input:** Thats why you're not leading.. bcoz you not paying for your fault.. you just leaving customers at their end &amp; be yourself remain in comfort zone.. My Pay Balance amount transfer in my bank account...
**Predicted Intent:** billing_issue
**Expected Intent:** general_inquiry
**Decision:** ESCALATE
**Expected Action:** AUTO_HANDLE
**Confidence:** 0.14
**Explanation:** Classifier predicted billing_issue instead of general_inquiry
**Hypothesis:** Similar vocabulary or semantic overlap between intents causes confusion.
**Proposed Improvement:** Add intent-specific discriminative features or use semantic embeddings.

--------------------------------------------------------------------------------

## Failure Mode 2: Intent Confusion: refund_request -> general_inquiry
**Frequency:** 1 occurrences

**Real Input:** não funciona! já tentei cancelar e não consigo. a página diz que cancelou, mas a compra continua lá!!!!...
**Predicted Intent:** general_inquiry
**Expected Intent:** refund_request
**Decision:** ESCALATE
**Expected Action:** ESCALATE
**Confidence:** 0.31
**Explanation:** Classifier predicted general_inquiry instead of refund_request
**Hypothesis:** Similar vocabulary or semantic overlap between intents causes confusion.
**Proposed Improvement:** Add intent-specific discriminative features or use semantic embeddings.

--------------------------------------------------------------------------------

## Failure Mode 3: Escalation Mismatch: AUTO_HANDLE -> ESCALATE
**Frequency:** 73 occurrences

**Real Input:** I’ve waited til past 8 o’clock now-here are the references: 67303131113645 &amp; 73303231558729 EVERY Hermes delivery gets delayed. No fun!...
**Predicted Intent:** order_status
**Expected Intent:** order_status
**Decision:** ESCALATE
**Expected Action:** AUTO_HANDLE
**Confidence:** 0.48
**Explanation:** System decided ESCALATE instead of AUTO_HANDLE
**Hypothesis:** Escalation policy may be too conservative.
**Proposed Improvement:** Adjust confidence thresholds or add evidence quality checks.

--------------------------------------------------------------------------------
