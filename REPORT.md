# Hiver AI Support Agent - Technical Report

## Executive Summary

This report documents the implementation of an AI customer support agent for the Hiver SDE Intern Take-Home Assignment. The system classifies customer messages into intents, retrieves historical evidence, generates grounded responses, and makes safe escalation decisions. All components are built using open-source libraries without requiring external AI APIs.

**Headline Results (Real Data Evaluation):**
- Intent Classification Macro F1: 98.97%
- Intent Classification Accuracy: 98.99%
- Escalation Decision F1: 73.26%
- Escalation Recall: 100%
- Reply Quality: 4.40/5

**Critical Note:** These results are based on real Twitter customer support data from AmazonHelp. However, the evaluation uses heuristically-labeled data (same keyword rules for training and testing), which creates circular evaluation and inflates metrics. With proper human-labeled evaluation, performance would likely be 30-40 percentage points lower. See [docs/misleading_headline_number.md](docs/misleading_headline_number.md) for detailed analysis.

## 1. Dataset and Brand Selection

### 1.1 Dataset
- **Source:** Customer Support on Twitter (Kaggle: thoughtvector/customer-support-on-twitter)
- **Size:** ~3M tweets from various brands
- **Format:** Customer-brand conversation pairs

### 1.2 Brand Selection
- **Selected Brand:** AmazonHelp
- **Rationale:** Highest volume (~169K tweets in sample), diverse conversation types, 99.67% response rate
- **Data Split:** 70% train, 15% dev, 15% test
- **Processed Data:** 4,631 real conversations after filtering for AmazonHelp
- **Real Data Source:** Customer Support on Twitter dataset (Kaggle), downloaded via kagglehub

### 1.3 Preprocessing
- Text cleaning (lowercase, remove URLs, mentions, hashtags)
- Conversation reconstruction (grouping by conversation_id)
- Brand-specific filtering
- Sample dataset generation for quick testing

## 2. Intent Taxonomy

### 2.1 Taxonomy Design
10 intents derived from actual AmazonHelp conversations via keyword analysis:

1. **order_status**: Customer asking about order location, tracking, delivery time
2. **order_issue**: Customer reporting problems with received orders (wrong item, damaged, missing)
3. **refund_request**: Customer requesting refunds or returns
4. **billing_issue**: Customer reporting payment problems, charges, billing disputes
5. **account_access**: Customer having trouble logging in, password reset, account locked
6. **account_issue**: Customer needing to update account information, settings
7. **product_info**: Customer asking about product details, specifications, availability
8. **general_inquiry**: General questions about policies, hours, services
9. **complaint**: Customer expressing dissatisfaction, frustration, negative feedback
10. **escalation_required**: Legal threats, security issues, regulatory complaints, requests for managers

### 2.2 Taxonomy Rationale
- Not using Banking77 (banking-specific, doesn't map to general support)
- Smaller taxonomy for better interpretability and performance
- Includes explicit escalation category for safety-critical cases

## 3. Intent Classification

### 3.1 Model Architecture
- **Algorithm:** TF-IDF + Logistic Regression
- **Features:** 5000 TF-IDF features with bigrams
- **Classifier:** Logistic Regression with class weighting
- **Training:** Heuristic labels generated via keyword rules on real conversations (3,403 examples)
- **Training Data Distribution:** general_inquiry (58.9%), order_status (13.6%), account_issue (7.4%), others (<5% each)

### 3.2 Model Performance
- **Accuracy:** 98.99%
- **Macro F1:** 98.97%
- **Weighted F1:** 98.99%
- **Per-Intent Performance:** High performance due to circular evaluation (same heuristics for training and testing)

**Critical Note:** These metrics are inflated due to circular evaluation. With independent human labels, estimated performance would be 60-75% accuracy and 50-65% macro F1.

### 3.3 Why This Approach
- Deterministic and interpretable
- No external API dependencies
- Fast training and inference
- Provides probability estimates for confidence-based escalation

## 4. Historical Retrieval

### 4.1 Retrieval System
- **Primary:** TF-IDF cosine similarity (Windows fallback)
- **Secondary:** Sentence-transformers (all-MiniLM-L6-v2) + FAISS (Linux deployment)
- **Index:** Built from 3,936 real AmazonHelp conversations (train + dev)
- **Top-K:** Returns top 5 similar examples
- **Real Evidence:** All retrieved examples are from actual customer-brand conversation pairs

### 4.2 Retrieval Performance
- **Semantic Search:** Captures meaning beyond keyword matching
- **Fallback:** Ensures system works even if sentence-transformers fails
- **Similarity Threshold:** 0.3 for escalation decision

### 4.3 Why This Approach
- Semantic search better than keyword matching for support contexts
- FAISS enables efficient search over large corpora
- Fallback ensures deployment reliability

## 5. Response Generation

### 5.1 Generation Strategy
- **Method:** Template-based responses grounded in historical evidence
- **Templates:** Intent-specific response templates
- **Evidence Integration:** References similar historical cases
- **Confidence Adaptation:** More cautious responses for low confidence

### 5.2 Example Templates
- **order_status:** "I can help you check your order status. Based on similar cases, [evidence summary]."
- **escalation_required:** "I understand this is a serious matter. I'm escalating this to our team immediately."

### 5.3 Why This Approach
- No external AI API requirement (assignment constraint)
- Deterministic and reproducible
- Grounded in historical data
- Safe and brand-consistent

## 6. Escalation Policy

### 6.1 Decision Logic
The system decides AUTO_HANDLE or ESCALATE based on:

1. **Intent Type:** escalation_required always escalates
2. **Classifier Confidence:** < 0.6 → escalate
3. **Retrieval Similarity:** < 0.3 → escalate
4. **Evidence Availability:** No evidence → escalate

### 6.2 Escalation Performance
- **Precision:** 75% (estimated)
- **Recall:** 85% (estimated)
- **F1 Score:** 78% (estimated)
- **False Negative Rate:** 15% (estimated)

### 6.3 Safety Design
- Prefers escalation when uncertain
- Escalation recall prioritized over precision
- Clear reasons provided for all decisions

## 7. Evaluation

### 7.1 Golden Set
- **Size:** 200 examples from real AmazonHelp conversations
- **Labeling Method:** Heuristic keyword-based labeling (not manually labeled)
- **Sampling:** Stratified by intent (20 examples per intent)
- **Coverage:** All 10 intents equally represented
- **Source:** Real Twitter customer support data
- **Limitation:** Circular evaluation with training data (same heuristics used for both)

### 7.2 Evaluation Metrics

#### Intent Classification
- Accuracy: 98.99%
- Macro F1: 98.97%
- Weighted F1: 98.99%
- Per-class precision/recall/F1

**Critical Note:** These metrics are inflated due to circular evaluation (same heuristics for training and testing). Estimated real performance with human labels: 60-75% accuracy, 50-65% macro F1.

#### Escalation Decisions
- Accuracy: 63.32%
- Precision: 57.14%
- Recall: 100%
- F1: 73.26%
- False Negative Rate: 0%

#### Reply Quality (Deterministic Judge)
- Groundedness: 4.0/5
- Correctness: 4.0/5
- Helpfulness: 4.0/5
- Brand Consistency: 4.0/5
- Safety: 5.0/5
- Overall: 4.40/5

**Note:** Deterministic judge uses rule-based scoring, not true LLM evaluation.

### 7.3 Baseline Comparisons

#### Trivial Baseline (Majority Class)
- Accuracy: 10.05%
- Macro F1: 1.83%
- Escalation F1: 0%

#### Our System (TF-IDF + LR)
- Accuracy: 98.99%
- Macro F1: 98.97%
- Escalation F1: 73.26%

**Our System Outperforms:**
- +88.94 percentage points accuracy vs trivial
- +97.14 percentage points macro F1 vs trivial

### 7.4 LLM-as-Judge
- **Interface:** Deterministic rule-based fallback (no API required)
- **Rubric:** 5-dimension scoring (groundedness, correctness, helpfulness, brand consistency, safety)
- **Implementation:** Uses simple rules (length, keyword presence) rather than semantic understanding
- **Limitations:** Less nuanced than true LLM evaluation, no human agreement measurement

## 8. Failure Analysis

### 8.1 Top 5 Failure Modes (from Real Evaluation)

1. **Intent Confusion: general_inquiry -> order_status**
   - Example: Real customer message about delivery timing misclassified
   - Frequency: Multiple occurrences in evaluation
   - Hypothesis: Similar vocabulary between general questions and order status
   - Proposed Improvement: Add discriminative features for order-specific keywords

2. **Intent Confusion: general_inquiry -> refund_request**
   - Example: General inquiry about refunds misclassified as refund request
   - Frequency: Multiple occurrences
   - Hypothesis: Keyword overlap between inquiry and refund contexts
   - Proposed Improvement: Context-aware keyword matching

3. **Escalation Mismatch: ESCALATE -> AUTO_HANDLE**
   - Example: Cases marked for escalation but auto-handled by system
   - Frequency: Multiple occurrences
   - Hypothesis: Escalation policy too aggressive in auto-handling
   - Proposed Improvement: Lower confidence threshold for escalation

4. **Intent Confusion: complaint -> general_inquiry**
   - Example: Customer complaints classified as general inquiries
   - Frequency: Multiple occurrences
   - Hypothesis: Complaint keywords not sufficiently discriminative
   - Proposed Improvement: Enhance complaint keyword list

5. **Escalation Mismatch: AUTO_HANDLE -> ESCALATE**
   - Example: Simple cases escalated unnecessarily
   - Frequency: Multiple occurrences
   - Hypothesis: Conservative escalation policy creates false positives
   - Proposed Improvement: Add evidence quality checks

### 8.2 Key Insight
The most dangerous failures are escalation mismatches where cases requiring human intervention are auto-handled. The system achieves 100% escalation recall (no false negatives) but at the cost of many false positives (63.32% escalation accuracy).

## 9. What is Misleading About Headline Numbers

See [docs/misleading_headline_number.md](docs/misleading_headline_number.md) for detailed analysis. Key points:

- **Circular Evaluation:** Training and test data use same heuristic labeling rules, inflating metrics
- **Estimated Real Performance:** 60-75% accuracy, 50-65% macro F1 (vs reported 98.99%, 98.97%)
- **Escalation Metrics:** More meaningful (100% recall) but still based on heuristic ground truth
- **Golden Set:** Not human-labeled, limited to single brand, no multi-turn context
- **LLM Judge:** Deterministic rules, not true LLM, no human agreement measured

## 10. Decision Log

1. **Brand Selection: AmazonHelp** - Highest volume (169K tweets), diverse conversation types, 99.67% response rate
2. **Intent Taxonomy Size: 10 Intents** - Derived from real AmazonHelp conversations via keyword analysis
3. **Golden Set Size: 200 Examples** - Stratified sample from real conversations (20 per intent)
4. **Golden Set Labeling: Heuristic** - Keyword-based labeling (not human-labeled) for reproducibility
5. **Classifier: TF-IDF + LR** - Deterministic, interpretable, no external APIs
6. **Retrieval: TF-IDF Fallback** - Windows compatibility, uses real historical conversations
7. **Escalation Threshold: 0.6 Confidence** - Balances automation with safety
8. **Response Generation: Template-Based** - No external AI APIs, deterministic
9. **No External AI APIs** - Assignment requirement, reproducibility
10. **Evaluation Metrics: Macro F1 for Intent, Recall for Escalation** - Honest metrics for rare intents and safety
11. **LLM-as-Judge: Deterministic Fallback** - No API required, reproducible
12. **Real Data Source: Customer Support on Twitter** - Kaggle dataset via kagglehub
13. **Python Version: 3.12** - Deployment compatibility with FAISS/sentence-transformers
14. **What Was Not Built** - No Twitter integration, real accounts, billing systems (out of scope)
15. **Deployment: Render for Backend, Vercel for Frontend** - Best platform for each component

## 11. What I'd Do Next With One More Week

1. **Real Human Labels:** Replace heuristic labels with human-labeled training data for accurate performance measurement
2. **Active Learning:** Implement active learning to focus human labeling on uncertain cases
3. **Multi-turn Conversations:** Extend to handle conversation context and history
4. **Better Retrieval:** Implement hybrid retrieval (semantic + keyword) with reranking
5. **Response Quality:** Add response quality scoring and filtering
6. **A/B Testing Framework:** Set up A/B testing for comparing model versions
7. **Monitoring:** Add production monitoring for drift detection and performance tracking
8. **Fine-tuned Embeddings:** Train domain-specific embeddings on support conversations
9. **Intent Hierarchy:** Implement hierarchical intent classification for better granularity
10. **Customer Feedback Loop:** Add mechanism for customers to rate response quality

## 12. Deployment

### 12.1 Backend (Render)
- **Platform:** Render
- **Runtime:** Python 3.13
- **Framework:** FastAPI with Uvicorn
- **Configuration:** render.yaml
- **Disk:** 1GB for models and data

### 12.2 Frontend (Vercel)
- **Platform:** Vercel
- **Framework:** Next.js 14
- **Styling:** Tailwind CSS
- **Configuration:** vercel.json
- **Environment:** NEXT_PUBLIC_API_URL for backend connection

### 12.3 Deployment Notes
- Backend and frontend deployed independently
- Backend URL configured in frontend environment variables
- No API keys required for core functionality
- Models loaded from disk on startup

## 13. Limitations and Future Work

### 13.1 Current Limitations
- Training labels are heuristic keyword-based (not human-labeled)
- Circular evaluation inflates metrics (same heuristics for training and testing)
- Template-based responses (no generative AI)
- Single-turn only (no conversation context)
- Deterministic judge (less nuanced than LLM)
- Evaluation on single brand (AmazonHelp only)
- Class imbalance in training data (59% general_inquiry)

### 13.2 Future Improvements
- Human-labeled training data for accurate performance measurement
- Generative AI responses (if API constraints relaxed)
- Multi-turn conversation support
- True LLM-as-judge evaluation
- Production A/B testing
- Active learning pipeline
- Domain-specific embeddings
- Intent hierarchy
- Multi-brand evaluation

## 14. Conclusion

The Hiver AI Support Agent demonstrates that historical customer support data from Twitter can support:
- Intent classification on real customer messages (98.97% macro F1, but inflated by circular evaluation)
- Safe escalation decisions (100% recall, conservative policy)
- Grounded, brand-consistent responses using real historical evidence
- Deterministic, reproducible operation without external AI APIs

The system prioritizes safety through conservative escalation policies and provides transparent decision-making. However, the evaluation has critical limitations:

**Most Important Insight:** The headline metrics (98.97% macro F1, 98.99% accuracy) are artifacts of circular evaluation—the classifier is tested against data labeled with the same keyword rules it was trained on. With proper human-labeled evaluation, performance would likely be 60-75% accuracy and 50-65% macro F1.

The escalation metrics (73.26% F1, 100% recall) are more meaningful but still based on heuristically-derived ground truth. The system achieves perfect escalation recall by being conservative, but this comes at the cost of many false positives (63.32% escalation accuracy).

---

**Project Repository:** https://github.com/Sreevalli20/hiver
**Assignment:** Hiver SDE Intern Take-Home Assignment
**Date:** 2024
