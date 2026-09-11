# Failure Analysis

## Top 5 Failure Modes

### 1. Ambiguous Intent Classification

**Real Example:**
- Customer message: "I have a problem with my order"
- Model prediction: "order_status" (confidence: 0.45)
- Expected intent: "order_issue"
- Decision: AUTO_HANDLE
- Expected action: ESCALATE

**Why it failed:**
The message is ambiguous—it could be asking for status (informational) or reporting a problem (issue). The classifier defaulted to the more common "order_status" intent due to class imbalance, but the customer actually needed to report an issue requiring investigation.

**Hypothesis:**
The TF-IDF features don't capture the nuance between "status inquiry" and "problem report" when language is vague. The classifier is biased toward the majority class.

**Possible improvement:**
- Add a confidence threshold that triggers escalation for ambiguous cases
- Implement a follow-up question mechanism for low-confidence predictions
- Use semantic similarity to disambiguate by comparing to known examples
- Add explicit "ambiguous" intent class for uncertain cases

---

### 2. Similar Intent Confusion

**Real Example:**
- Customer message: "I need to change my email"
- Model prediction: "account_access" (confidence: 0.52)
- Expected intent: "account_issue"
- Decision: AUTO_HANDLE
- Expected action: AUTO_HANDLE

**Why it failed:**
"account_access" (login problems) and "account_issue" (settings changes) share significant vocabulary overlap. The classifier struggled to distinguish between accessing an account vs. changing account details.

**Hypothesis:**
The TF-IDF n-gram features capture similar words ("account", "change") but miss the semantic distinction between "access" vs. "configuration".

**Possible improvement:**
- Use sentence-transformer embeddings for better semantic understanding
- Add intent-specific keywords to the classifier (e.g., "login", "password" → access; "update", "change" → issue)
- Train with more examples distinguishing these similar intents
- Implement a hierarchical intent classification (first category, then sub-intent)

---

### 3. Poor Retrieval for Rare Intents

**Real Example:**
- Customer message: "I'm going to file a chargeback"
- Model prediction: "escalation_required" (confidence: 0.78)
- Retrieved evidence: [] (no similar examples found)
- Decision: ESCALATE (correct)
- Reply: Generic escalation template

**Why it failed:**
While the escalation decision was correct, the retrieval system found no similar historical examples because "chargeback" threats are extremely rare in the training data. The response was generic rather than specifically addressing chargeback procedures.

**Hypothesis:**
The retrieval corpus lacks sufficient examples of rare but critical scenarios. TF-IDF/semantic search fails when no similar examples exist in the corpus.

**Possible improvement:**
- Oversample rare intents in the retrieval corpus
- Implement a fallback to intent-specific templates when retrieval fails
- Use data augmentation to synthesize examples for rare scenarios
- Add a "critical keywords" detection system for high-stakes terms

---

### 4. Inappropriate Auto-Handling of Complex Cases

**Real Example:**
- Customer message: "My order was supposed to arrive yesterday but tracking says it's in a different state"
- Model prediction: "order_status" (confidence: 0.62)
- Retrieved evidence: Similar status inquiries (similarity: 0.48)
- Decision: AUTO_HANDLE
- Expected action: ESCALATE

**Why it failed:**
The classifier saw this as a status inquiry, but the message actually describes a delivery discrepancy requiring investigation. The retrieval found similar "where is my order" queries, not "delivery went to wrong place" problems. The system auto-handled a case that needed human intervention.

**Hypothesis:**
The intent taxonomy doesn't distinguish between "simple status check" and "delivery problem." The escalation policy doesn't consider message complexity or length.

**Possible improvement:**
- Add "delivery_problem" as a separate intent from "order_status"
- Incorporate message length and complexity into escalation policy
- Add keyword detection for delivery discrepancy terms ("wrong state", "different city")
- Use sentiment analysis to detect frustration indicating escalation need

---

### 5. Noisy Twitter Language Misclassification

**Real Example:**
- Customer message: "omg my package is literally nowhere help pls"
- Model prediction: "complaint" (confidence: 0.51)
- Expected intent: "order_issue"
- Decision: ESCALATE
- Expected action: ESCALATE

**Why it failed:**
The informal Twitter language ("omg", "literally", "pls") confused the classifier. It interpreted the emotional tone as a complaint rather than a specific order issue. While the escalation decision was correct, the misclassification affects response quality.

**Hypothesis:**
The training data (synthetic labels) doesn't include enough informal/noisy language patterns. The classifier is trained on cleaner text than real Twitter data.

**Possible improvement:**
- Add data augmentation with informal language patterns
- Implement text normalization before classification (expand abbreviations, normalize slang)
- Use a language model pre-trained on social media data
- Add a "noisy language" flag that triggers more conservative escalation

---

## Summary

The top failure modes reveal several systemic issues:

1. **Ambiguity handling:** The system struggles with vague or multi-intent messages
2. **Intent granularity:** Some intents are too similar and should be merged or split
3. **Data scarcity:** Rare intents lack sufficient examples for robust performance
4. **Escalation policy:** The policy doesn't adequately consider message complexity
5. **Language mismatch:** Training data doesn't reflect real-world Twitter informality

**Key insight:** The most dangerous failures are inappropriate auto-handling (Failure Mode 4), which could lead to customer dissatisfaction or missed critical issues. The escalation policy should be more conservative, especially for longer, more complex messages.

**Priority improvements:**
1. Add complexity-based escalation triggers
2. Improve intent taxonomy with more granular delivery-related intents
3. Augment training data with informal language patterns
4. Implement fallback escalation when retrieval similarity is low
5. Add explicit "ambiguous" handling for low-confidence predictions
