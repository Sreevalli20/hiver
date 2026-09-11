# Decision Log

## 1. Brand Selection: AmazonHelp

**Decision:** Selected AmazonHelp as the target brand from the Customer Support on Twitter dataset.

**Why:** AmazonHelp has the highest volume of customer support tweets (~280K tweets), diverse conversation types, and good conversation completeness. The brand deals with order issues, refunds, account access, and general inquiries—providing a rich variety of support scenarios.

**Tradeoff:** While AmazonHelp has high volume, the data is also noisier than smaller brands. However, the volume advantage outweighs the noise for training robust models.

---

## 2. Intent Taxonomy Size: 10 Intents

**Decision:** Created a taxonomy with 10 intents rather than using Banking77's 77 intents.

**Why:** Banking77 is banking-specific and doesn't map well to general customer support. A smaller, brand-specific taxonomy derived from actual conversations is more interpretable and sufficient for the use case. Ten intents cover the major support categories without overcomplicating the classification task.

**Tradeoff:** Fewer intents mean some nuance is lost (e.g., "delivery_problem" vs "order_issue"). However, this improves model performance and interpretability, which is more important for this evaluation.

---

## 3. Golden Set Size: 200 Examples

**Decision:** Created a golden evaluation set with exactly 200 hand-labelled examples.

**Why:** The assignment requires 150-250 examples. 200 provides sufficient statistical power for evaluation while remaining manageable for manual labeling. The set includes balanced representation of all intents, difficulty levels, and escalation-worthy cases.

**Tradeoff:** 200 examples is small compared to the full dataset, but it's sufficient for evaluation purposes and allows for careful, high-quality labeling. A larger set would require more time without proportional evaluation benefit.

---

## 4. Golden Set Sampling Strategy

**Decision:** Used stratified sampling by intent and difficulty rather than random sampling.

**Why:** Random sampling would over-represent common intents and easy cases. Stratified sampling ensures all intents are represented, including rare ones like "escalation_required." This provides a more honest evaluation of performance across the full intent spectrum.

**Tradeoff:** Stratified sampling doesn't reflect real-world class imbalance, so accuracy metrics will be lower than in production. However, this is more appropriate for evaluation—we want to measure performance on rare, critical intents, not just common ones.

---

## 5. Classifier: TF-IDF + Logistic Regression

**Decision:** Used TF-IDF with Logistic Regression as the primary classifier.

**Why:** This is a strong, interpretable baseline that works well for text classification. It's deterministic, fast to train, and doesn't require external APIs. Logistic Regression provides probability estimates useful for confidence-based escalation.

**Tradeoff:** More complex models (e.g., BERT, fine-tuned transformers) would likely achieve higher accuracy. However, they require more compute, are harder to deploy, and the assignment constraints prohibit external APIs. TF-IDF+LR is the best balance of performance and simplicity.

---

## 6. Retrieval: Sentence-Transformers + FAISS with TF-IDF Fallback

**Decision:** Implemented semantic search using sentence-transformers and FAISS, with TF-IDF cosine similarity as a fallback.

**Why:** Semantic search captures meaning better than keyword matching, which is crucial for finding similar historical support cases. FAISS enables efficient similarity search over large corpora. The TF-IDF fallback ensures the system works even if sentence-transformers has deployment issues.

**Tradeoff:** Sentence-transformers adds model loading time and memory usage. The TF-IDF fallback is less accurate but more lightweight. The hybrid approach provides the best of both: accuracy when possible, reliability when needed.

---

## 7. Escalation Threshold: 0.6 Confidence

**Decision:** Set the classifier confidence threshold for auto-handling at 0.6.

**Why:** A threshold of 0.6 balances automation with safety. It allows confident predictions to be auto-handled while escalating uncertain cases. This is conservative enough to avoid dangerous auto-handling errors while still providing automation value.

**Tradeoff:** A higher threshold (e.g., 0.8) would be safer but reduce automation. A lower threshold (e.g., 0.4) would increase automation but risk more errors. 0.6 is a reasonable middle ground based on the classifier's calibration.

---

## 8. Response Generation: Template-Based

**Decision:** Used template-based response generation rather than generative AI.

**Why:** The assignment prohibits external AI APIs. Template-based responses are safe, deterministic, and grounded in historical patterns. They avoid hallucination and ensure brand consistency.

**Tradeoff:** Templates are less flexible and conversational than AI-generated responses. However, they're more reliable and appropriate for a support context where accuracy matters more than conversational flair.

---

## 9. No External AI APIs

**Decision:** Built the entire system without requiring any external AI API keys.

**Why:** The assignment explicitly prohibits paid LLM APIs (OpenAI, Gemini, Anthropic). Using open-source, local libraries ensures the system is reproducible and doesn't have ongoing costs or dependencies on third-party services.

**Tradeoff:** This limits response generation to templates rather than AI-generated text. However, this aligns with the goal of evaluating whether historical data alone can support grounded responses, not whether we can generate conversational AI.

---

## 10. Evaluation Metrics: Macro F1 for Intent, Recall for Escalation

**Decision:** Prioritized macro F1 for intent classification and recall for escalation decisions.

**Why:** Macro F1 treats all intents equally, which is important for rare intents. Escalation recall is critical because false negatives (auto-handling when should escalate) are dangerous—missing a legal threat or security issue is unacceptable.

**Tradeoff:** Accuracy would be higher due to class imbalance, but it's misleading. Macro F1 is lower but more honest. Escalation precision matters too, but recall is the safety-critical metric.

---

## 11. LLM-as-Judge: Deterministic Fallback

**Decision:** Implemented the LLM-as-judge with a deterministic rule-based fallback that doesn't require APIs.

**Why:** The core system must not require external APIs. A deterministic fallback ensures evaluation can run without credentials. The judge interface is designed to optionally plug in an LLM later if desired.

**Tradeoff:** The deterministic judge is less nuanced than a true LLM judge. However, it provides a baseline evaluation methodology that can be executed reproducibly without external dependencies.

---

## 12. Human Validation Sample: 50 Examples

**Decision:** Created a human validation sample of 50 replies for judge comparison.

**Why:** 50 examples provide sufficient data to measure human-judge agreement without requiring excessive manual effort. This sample is used to validate the judge's scoring methodology.

**Tradeoff:** 50 examples is a small sample for statistical significance. However, it's sufficient to identify major discrepancies between human and judge scoring, which is the goal of the comparison.

---

## 13. Python Version: 3.13 for Deployment

**Decision:** Used Python 3.13 for deployment compatibility with FAISS and sentence-transformers.

**Why:** Python 3.14 (initially specified) may have compatibility issues with FAISS/sentence-transformers on Render. Python 3.13 is known to work well with these libraries while being recent enough for modern features.

**Tradeoff:** Python 3.14 would be more cutting-edge, but deployment reliability is more important. The functionality (FAISS, sentence-transformers) takes priority over using the absolute latest Python version.

---

## 14. What Was Not Built

**Decision:** Explicitly did not build Twitter integration, real customer accounts, billing systems, authentication, or payment processing.

**Why:** The assignment is an evaluation of whether historical support data can support intent classification, grounded replies, and safe escalation—not a production customer support platform. Building real systems would be out of scope and introduce unnecessary complexity.

**Tradeoff:** The system is a demo/evaluation rather than a production platform. However, this aligns with the assignment's goal of evaluating the core ML/decision components, not building a full SaaS product.

---

## 15. Deployment: Render for Backend, Vercel for Frontend

**Decision:** Chose Render for backend deployment and Vercel for frontend deployment.

**Why:** Render has good Python support and is suitable for FastAPI backends. Vercel is optimized for Next.js and provides excellent frontend deployment. This separation allows independent scaling and deployment of each component.

**Tradeoff:** Using a single platform (e.g., Render for both) would be simpler. However, using the best platform for each component (Vercel for Next.js, Render for Python) provides better performance and developer experience.
